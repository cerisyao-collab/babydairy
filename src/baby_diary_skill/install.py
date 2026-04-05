#!/usr/bin/env python3
"""
Baby Diary Skill 安装脚本

将 baby_diary 技能安装到 OpenClaw 技能目录
"""

import os
import shutil
from pathlib import Path

# OpenClaw 默认技能目录
OPENCLAW_SKILL_DIRS = [
    Path.home() / ".openclaw" / "skills",
    Path("/usr/local/share/openclaw/skills"),
    Path("/opt/openclaw/skills"),
]

# 当前脚本所在目录
CURRENT_DIR = Path(__file__).parent

def find_openclaw_skill_dir():
    """查找 OpenClaw 技能目录"""
    # 检查环境变量
    env_dir = os.environ.get("OPENCLAW_SKILL_DIR")
    if env_dir:
        return Path(env_dir)

    # 检查默认位置
    for dir_path in OPENCLAW_SKILL_DIRS:
        if dir_path.exists():
            return dir_path

    # 如果都不存在，创建第一个
    default_dir = OPENCLAW_SKILL_DIRS[0]
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir

def install_skill():
    """安装技能到 OpenClaw"""
    target_dir = find_openclaw_skill_dir()
    dest_dir = target_dir / "baby_diary_skill"

    print(f"安装 baby_diary 技能到：{target_dir}")

    # 如果已存在，先删除
    if dest_dir.exists():
        print(f"删除已存在的版本...")
        shutil.rmtree(dest_dir)

    # 复制技能目录
    print(f"复制技能文件...")
    shutil.copytree(CURRENT_DIR, dest_dir)

    # 创建软链接（可选）
    # print(f"创建软链接...")
    # link_path = Path.home() / ".local" / "bin" / "baby_diary_skill"
    # link_path.parent.mkdir(parents=True, exist_ok=True)
    # if link_path.exists() or link_path.is_symlink():
    #     link_path.unlink()
    # link_path.symlink_to(dest_dir)

    print(f"""
╔═══════════════════════════════════════════════════════════╗
║  Baby Diary Skill 安装完成！                               ║
╠═══════════════════════════════════════════════════════════╣
║  安装位置：{dest_dir}
║                                                           ║
║  下一步：                                                  ║
║  1. 重启 OpenClaw 服务                                      ║
║  2. 使用 `openclaw skill list` 验证安装                    ║
║  3. 在 OpenClaw 配置中启用技能                             ║
╚═══════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    install_skill()
