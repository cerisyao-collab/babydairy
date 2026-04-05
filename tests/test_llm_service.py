"""Tests for LLM Service"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from src.services.llm_service import LLMService, SYSTEM_PROMPTS
from src.services.ai_analyzer import AnalysisResult, Status, MetricAnalysis, Issue


@pytest.fixture
def mock_analysis():
    """Create mock analysis result"""
    return AnalysisResult(
        status=Status.NORMAL,
        confidence=0.8,
        metrics={
            "milk_volume": MetricAnalysis(
                value=500, min=400, max=600, avg=500,
                status=Status.NORMAL,
                description="奶量500ml，处于正常范围"
            ),
        },
        issues=[
            Issue(
                type="long_interval",
                severity="low",
                description="平均喂养间隔4小时",
                metric="interval"
            ),
        ],
        recommendations=["建议缩短喂养间隔至3小时"],
        baby_age_days=15,
        feeding_data_summary={
            "total_milk": 500,
            "feeding_count": 8,
            "avg_interval": 4.0,
        },
    )


class TestLLMService:
    """Tests for LLMService class"""

    def test_init_with_settings(self):
        """Test LLM service initialization with default settings"""
        with patch("src.services.llm_service.settings") as mock_settings:
            mock_settings.dashscope_api_key = "test-key"
            mock_settings.qwen_model = "qwen-turbo"

            service = LLMService()

            assert service.api_key == "test-key"
            assert service.model == "qwen-turbo"

    def test_init_with_custom_params(self):
        """Test LLM service initialization with custom parameters"""
        service = LLMService(api_key="custom-key", model="qwen-plus")

        assert service.api_key == "custom-key"
        assert service.model == "qwen-plus"

    @patch("src.services.llm_service.Generation.call")
    def test_call_qwen_success(self, mock_call):
        """Test successful Qwen API call"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output.choices = [
            MagicMock(message=MagicMock(content="测试响应"))
        ]
        mock_call.return_value = mock_response

        service = LLMService(api_key="test-key")
        result = service._call_qwen("system prompt", "user prompt")

        assert result == "测试响应"
        mock_call.assert_called_once()

    @patch("src.services.llm_service.Generation.call")
    def test_call_qwen_error(self, mock_call):
        """Test Qwen API call error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.code = "InvalidParameter"
        mock_response.message = "参数错误"
        mock_call.return_value = mock_response

        service = LLMService(api_key="test-key")

        with pytest.raises(Exception) as exc_info:
            service._call_qwen("system prompt", "user prompt")

        assert "参数错误" in str(exc_info.value)

    def test_cache_key_generation(self):
        """Test cache key generation"""
        service = LLMService()

        key1 = service._get_cache_key("相同内容")
        key2 = service._get_cache_key("相同内容")
        key3 = service._get_cache_key("不同内容")

        assert key1 == key2
        assert key1 != key3

    def test_cache_response(self):
        """Test response caching"""
        from src.services.llm_service import _response_cache

        service = LLMService()
        cache_key = "test-key"

        service._cache_response(cache_key, "测试响应")

        assert cache_key in _response_cache
        assert _response_cache[cache_key]["response"] == "测试响应"

    def test_get_cached_response_valid(self):
        """Test getting valid cached response"""
        from src.services.llm_service import _response_cache

        service = LLMService()
        cache_key = "test-key"

        # Add fresh cache entry
        _response_cache[cache_key] = {
            "response": "缓存响应",
            "timestamp": datetime.now()
        }

        result = service._get_cached_response(cache_key)
        assert result == "缓存响应"

    def test_get_cached_response_expired(self):
        """Test getting expired cached response"""
        from src.services.llm_service import _response_cache

        service = LLMService()
        cache_key = "expired-key"

        # Add expired cache entry (> 1 hour)
        _response_cache[cache_key] = {
            "response": "过期响应",
            "timestamp": datetime.now() - timedelta(hours=2)
        }

        result = service._get_cached_response(cache_key)
        assert result is None

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_generate_analysis_text(self, mock_call, mock_analysis):
        """Test generating analysis text"""
        mock_call.return_value = "AI生成的分析文本"

        service = LLMService(api_key="test-key")
        result = service.generate_analysis_text(mock_analysis)

        assert result == "AI生成的分析文本"
        mock_call.assert_called_once()

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_generate_analysis_text_with_cache(self, mock_call, mock_analysis):
        """Test generating analysis text with cached response"""
        from src.services.llm_service import _response_cache

        # Pre-cache a response
        user_prompt = "test prompt"
        cache_key = "cached-key"
        _response_cache[cache_key] = {
            "response": "缓存的分析",
            "timestamp": datetime.now()
        }

        service = LLMService(api_key="test-key")

        # This should return cached response without calling API
        with patch.object(service, '_build_analysis_prompt', return_value=user_prompt):
            with patch.object(service, '_get_cache_key', return_value=cache_key):
                result = service.generate_analysis_text(mock_analysis)

        assert result == "缓存的分析"
        mock_call.assert_not_called()

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_generate_analysis_text_fallback(self, mock_call, mock_analysis):
        """Test fallback when LLM fails"""
        mock_call.side_effect = Exception("API失败")

        service = LLMService(api_key="test-key")
        result = service.generate_analysis_text(mock_analysis)

        # Should return fallback summary
        assert "正常" in result

    def test_build_analysis_prompt(self, mock_analysis):
        """Test building analysis prompt"""
        service = LLMService()
        prompt = service._build_analysis_prompt(mock_analysis)

        assert "宝宝年龄" in prompt
        assert "15" in prompt
        assert "总奶量" in prompt
        assert "500" in prompt

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_chat(self, mock_call):
        """Test chat functionality"""
        mock_call.return_value = "AI回答"

        service = LLMService(api_key="test-key")
        result = service.chat("宝宝吃多少合适?", {"baby_age_days": 15})

        assert result == "AI回答"
        mock_call.assert_called_once()

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_chat_with_context(self, mock_call):
        """Test chat with context"""
        mock_call.return_value = "AI回答"

        service = LLMService(api_key="test-key")
        result = service.chat(
            "宝宝奶量够吗?",
            context={
                "baby_age_days": 15,
                "today_milk": 500,
                "feeding_count": 8,
            }
        )

        assert result == "AI回答"
        # Check that context was included in prompt
        call_args = mock_call.call_args
        user_prompt = call_args[1]["messages"][1]["content"]
        assert "宝宝年龄" in user_prompt
        assert "今日奶量" in user_prompt

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_chat_error_fallback(self, mock_call):
        """Test chat error fallback"""
        mock_call.side_effect = Exception("API失败")

        service = LLMService(api_key="test-key")
        result = service.chat("测试问题")

        assert "抱歉" in result or "稍后" in result

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_generate_daily_report_summary(self, mock_call):
        """Test daily report summary generation"""
        mock_call.return_value = "今日喂养总结"

        service = LLMService(api_key="test-key")
        feeding_data = {"total_milk": 500, "feeding_count": 8}

        result = service.generate_daily_report_summary(feeding_data)

        assert result == "今日喂养总结"

    @patch("src.services.llm_service.LLMService._call_qwen")
    def test_generate_daily_report_summary_with_analysis(self, mock_call, mock_analysis):
        """Test daily report summary with analysis"""
        mock_call.return_value = "今日喂养分析总结"

        service = LLMService(api_key="test-key")
        feeding_data = {"total_milk": 500, "feeding_count": 8}

        result = service.generate_daily_report_summary(feeding_data, mock_analysis)

        assert result == "今日喂养分析总结"

    def test_generate_fallback_summary(self, mock_analysis):
        """Test fallback summary generation"""
        service = LLMService()
        result = service._generate_fallback_summary(mock_analysis)

        assert "正常" in result


class TestSystemPrompts:
    """Tests for system prompts"""

    def test_feeding_analysis_prompt_exists(self):
        """Test feeding analysis prompt exists"""
        assert "feeding_analysis" in SYSTEM_PROMPTS
        prompt = SYSTEM_PROMPTS["feeding_analysis"]

        assert "新生儿喂养顾问" in prompt
        assert "建议" in prompt

    def test_chat_prompt_exists(self):
        """Test chat prompt exists"""
        assert "chat" in SYSTEM_PROMPTS
        prompt = SYSTEM_PROMPTS["chat"]

        assert "喂养顾问助手" in prompt
        assert "友好" in prompt

    def test_prompt_has_constraints(self):
        """Test prompts have medical constraints"""
        feeding_prompt = SYSTEM_PROMPTS["feeding_analysis"]

        # Should contain disclaimer language
        assert "不能替代医生诊断" in feeding_prompt
        assert "建议咨询医生" in feeding_prompt