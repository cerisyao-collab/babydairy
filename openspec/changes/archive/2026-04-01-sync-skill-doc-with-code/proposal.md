## Why

当前 baby-diary 技能的文档与代码存在严重不一致：
1. **代码位置不一致**：`~/.openclaw/skills/baby_diary_skill/`（完整版）与 `src/baby-diary/`（简化版）功能差异大
2. **文档缺失**：SKILL.md 只记录了 8 个函数，但代码有 20+ 个公开函数
3. **功能未文档化**：图片功能、宝宝配置、重复检测、文件锁等功能缺少文档说明

## What Changes

- **补充缺失函数文档**：添加图片查看、宝宝配置、重复检测等函数说明
- **统一代码版本**：将 openclaw 版本的完整功能同步到 src/baby-diary/
- **更新 README.md**：确保两个位置的 README 内容一致
- **添加 __all__ 导出列表**：在 src/baby-diary/__init__.py 中添加完整的导出列表

## Capabilities

### New Capabilities

- `skill-doc-completeness`: 补充缺失的函数文档
- `code-sync`: 统一不同位置的代码版本

### Modified Capabilities

- `baby-diary-skill`: SKILL.md 添加完整函数说明

## Impact

- **受影响文件**:
  - `.claude/skills/baby-diary/SKILL.md`
  - `~/.openclaw/skills/baby_diary_skill/SKILL.md`
  - `~/.openclaw/skills/baby_diary_skill/README.md`
  - `src/baby-diary/__init__.py`（需同步完整功能）
  - `src/baby-diary/README.md`
- **向后兼容**：纯文档更新和代码同步，不影响现有 API
