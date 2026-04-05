"""LLM Service for Qwen (通义千问) integration

Provides AI-powered text generation for feeding analysis.
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import lru_cache

import dashscope
from dashscope import Generation
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings
from src.services.ai_analyzer import AnalysisResult


logger = logging.getLogger(__name__)


# Cache for LLM responses (simple in-memory cache)
_response_cache: Dict[str, Dict[str, Any]] = {}


# System prompts for different scenarios
SYSTEM_PROMPTS = {
    "feeding_analysis": """你是一个专业的新生儿喂养顾问，负责分析宝宝的喂养数据并给出建议。

重要规则:
1. 你提供的建议仅供参考，不能替代医生诊断
2. 使用温和、鼓励的语气，避免让父母焦虑
3. 建议要具体、可执行
4. 如果数据异常明显，建议就医
5. 避免使用"必须"、"一定"、"确诊"、"疾病"等词汇
6. 推荐使用"建议"、"可以考虑"、"建议咨询医生"等词汇

输出格式要求:
- 第一句: 简明的状态判断
- 第二句: 具体问题说明
- 第三句: 可执行的建议

保持回答简洁，不超过100字。""",

    "chat": """你是一个友好的新生儿喂养顾问助手。

你的职责是帮助新手父母解决喂养相关问题。请注意:
1. 提供的信息仅供参考，不能替代医生诊断
2. 使用温和、友善的语气
3. 回答要具体、实用
4. 如有健康疑虑，建议咨询医生

回答保持简洁友好。"""
}


class LLMService:
    """Service for LLM-based text generation using Qwen"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM service.

        Args:
            api_key: DashScope API key (defaults to settings)
            model: Model name (defaults to settings)
        """
        self.api_key = api_key or settings.dashscope_api_key
        self.model = model or settings.qwen_model

        if self.api_key:
            dashscope.api_key = self.api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _call_qwen(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 500
    ) -> str:
        """
        Call Qwen API with retry logic.

        Args:
            system_prompt: System instruction
            user_prompt: User input
            max_tokens: Maximum output tokens

        Returns:
            Generated text

        Raises:
            Exception: If API call fails after retries
        """
        try:
            response = Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                result_format='message'
            )

            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                logger.error(f"Qwen API error: {response.code} - {response.message}")
                raise Exception(f"Qwen API error: {response.message}")

        except Exception as e:
            logger.error(f"Failed to call Qwen API: {e}")
            raise

    def _get_cache_key(self, content: str) -> str:
        """Generate cache key from content"""
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if exists and not expired"""
        if cache_key in _response_cache:
            cached = _response_cache[cache_key]
            # Check if cache is still valid (1 hour)
            if datetime.now() - cached["timestamp"] < timedelta(hours=1):
                return cached["response"]
        return None

    def _cache_response(self, cache_key: str, response: str) -> None:
        """Cache response with timestamp"""
        _response_cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now()
        }

    def generate_analysis_text(self, analysis: AnalysisResult) -> str:
        """
        Generate natural language analysis text.

        Args:
            analysis: Analysis result from FeedingAnalyzer

        Returns:
            AI-generated analysis text
        """
        # Build user prompt with analysis data
        user_prompt = self._build_analysis_prompt(analysis)

        # Check cache
        cache_key = self._get_cache_key(user_prompt)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached

        try:
            # Call LLM
            response = self._call_qwen(
                system_prompt=SYSTEM_PROMPTS["feeding_analysis"],
                user_prompt=user_prompt
            )

            # Cache response
            self._cache_response(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"Failed to generate analysis text: {e}")
            # Fallback to rule-based summary
            return self._generate_fallback_summary(analysis)

    def _build_analysis_prompt(self, analysis: AnalysisResult) -> str:
        """Build user prompt for analysis generation"""
        parts = []

        # Baby info
        if analysis.baby_age_days:
            parts.append(f"宝宝年龄: {analysis.baby_age_days}天")

        # Feeding data summary
        if analysis.feeding_data_summary:
            data = analysis.feeding_data_summary
            parts.append(f"今日喂养数据:")
            parts.append(f"- 总奶量: {data.get('total_milk', 0)}ml")
            parts.append(f"- 喂养次数: {data.get('feeding_count', 0)}次")
            if data.get('avg_interval'):
                parts.append(f"- 平均间隔: {data.get('avg_interval'):.1f}小时")

        # Metrics analysis
        parts.append("\n指标分析:")
        for metric_name, metric in analysis.metrics.items():
            parts.append(f"- {metric.description}")

        # Issues
        if analysis.issues:
            parts.append("\n发现的问题:")
            for issue in analysis.issues:
                parts.append(f"- {issue.description}")

        # Recommendations
        if analysis.recommendations:
            parts.append("\n建议:")
            for rec in analysis.recommendations:
                parts.append(f"- {rec}")

        return "\n".join(parts)

    def _generate_fallback_summary(self, analysis: AnalysisResult) -> str:
        """Generate fallback summary without LLM"""
        status_text = {
            "normal": "正常",
            "low": "偏低",
            "high": "偏高"
        }

        summary = f"今日喂养状态：{status_text.get(analysis.status.value, '未知')}"

        if analysis.issues:
            summary += f"。发现问题：{', '.join(i.description for i in analysis.issues[:2])}"

        if analysis.recommendations:
            summary += f"。{analysis.recommendations[0]}"

        return summary

    def chat(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Answer user question with context.

        Args:
            question: User's question
            context: Additional context (baby info, feeding data)

        Returns:
            AI-generated response
        """
        # Build prompt with context
        user_prompt = question

        if context:
            context_parts = []
            if "baby_age_days" in context:
                context_parts.append(f"宝宝年龄: {context['baby_age_days']}天")
            if "today_milk" in context:
                context_parts.append(f"今日奶量: {context['today_milk']}ml")
            if "feeding_count" in context:
                context_parts.append(f"喂养次数: {context['feeding_count']}次")

            if context_parts:
                user_prompt = f"背景信息:\n{chr(10).join(context_parts)}\n\n问题: {question}"

        # Check cache
        cache_key = self._get_cache_key(user_prompt)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached

        try:
            response = self._call_qwen(
                system_prompt=SYSTEM_PROMPTS["chat"],
                user_prompt=user_prompt
            )

            self._cache_response(cache_key, response)
            return response

        except Exception as e:
            logger.error(f"Failed to generate chat response: {e}")
            return "抱歉，暂时无法回答您的问题。请稍后再试。"

    def generate_daily_report_summary(
        self,
        feeding_data: Dict[str, Any],
        analysis: Optional[AnalysisResult] = None
    ) -> str:
        """
        Generate daily report summary.

        Args:
            feeding_data: Feeding data summary
            analysis: Optional analysis result

        Returns:
            AI-generated summary
        """
        user_prompt = f"""请为以下喂养数据生成每日报告摘要:

总奶量: {feeding_data.get('total_milk', 0)}ml
喂养次数: {feeding_data.get('feeding_count', 0)}次
"""

        if analysis:
            user_prompt += f"\n分析状态: {analysis.status.value}"
            if analysis.issues:
                user_prompt += f"\n问题: {', '.join(i.description for i in analysis.issues)}"

        user_prompt += "\n\n请生成一段简短的每日总结(不超过50字)。"

        try:
            return self._call_qwen(
                system_prompt=SYSTEM_PROMPTS["feeding_analysis"],
                user_prompt=user_prompt,
                max_tokens=100
            )
        except Exception:
            return f"今日喂养{feeding_data.get('feeding_count', 0)}次，总奶量{feeding_data.get('total_milk', 0)}ml。"