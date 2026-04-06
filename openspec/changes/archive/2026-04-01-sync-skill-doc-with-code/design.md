## Context

当前 baby-diary 技能存在多处不一致：

**代码位置差异**：
| 功能 | ~/.openclaw/skills/ | src/baby-diary/ |
|------|---------------------|-----------------|
| 文件锁 | ✓ | ✗ |
| 缓存失效 | ✓ | ✗ |
| daily_summary | ✓ | ✗ |
| compare_with_standards | ✓ | ✗ |
| 图片功能 | ✓ | ✗ |
| baby_config | ✓ | ✗ |
| 重复检测 | ✓ | ✗ |

**文档缺失**：
- SKILL.md 只记录 8 个函数，__all__ 导出 20+ 个函数
- 图片查看功能完全未文档化
- 宝宝配置功能未文档化
- 重复检测功能未文档化

## Goals / Non-Goals

**Goals:**
- 补充 SKILL.md 中缺失的函数文档
- 统一两个位置的 README.md 内容
- 将 openclaw 版本的完整代码同步到 src/baby-diary/

**Non-Goals:**
- 不添加新功能
- 不修改现有 API 行为
- 不改变数据存储格式

## Decisions

### 1. 文档优先级

**决策**：以 openclaw 版本的代码为准，补充 SKILL.md 文档

**理由**：
- openclaw 版本是实际运行的版本
- 功能更完整，用户体验更好

### 2. 代码同步策略

**决策**：将 openclaw 版本的 __init__.py 复制到 src/baby-diary/

**理由**：
- 确保开发环境与运行环境一致
- 避免功能差异导致的混淆

### 3. 文档结构

**决策**：在 SKILL.md 中按功能分组添加缺失函数文档

**分组**：
- 核心 CRUD：record_* 函数
- 每日总结：daily_summary, compare_with_standards
- 图片功能：image_view, list_images, image_gallery, generate_thumbnail
- 配置管理：get_baby_config, set_baby_config
- 工具函数：refresh_index, check_duplicate_records 等

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| src 版本同步后体积增大 | 保持不变，仅同步必要功能 |
| 文档过长影响阅读 | 按功能分组，使用清晰标题 |
| 代码同步可能导致冲突 | 先备份，再同步，最后验证 |

## Migration Plan

1. 备份现有文件
2. 补充 SKILL.md 缺失函数文档
3. 同步 openclaw 代码到 src/baby-diary/
4. 同步两个 README.md
5. 验证功能正常
