"""应用路径管理 —— 适配 PyInstaller 打包。

打包后：
- app_root = sys._MEIPASS（只读资源：static/templates/skills 等）
- data_root = %APPDATA%/laoma-bid（可写：data/projects/chroma_db/uploads/输出）
开发时两者都 = 项目根，行为与现在完全一致。

可写目录可用环境变量 BIDMASTER_DATA_DIR 覆盖（测试/多实例时有用）。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _project_root() -> Path:
    # pathkit/__init__.py → 开源仓根
    return Path(__file__).resolve().parent.parent


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False)) or bool(getattr(sys, "_MEIPASS", None))


def app_root() -> Path:
    """只读资源根：打包后为 _MEIPASS，开发为项目根。"""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return _project_root()


def data_root() -> Path:
    """可写数据根：打包后 %APPDATA%/laoma-bid（可用 BIDMASTER_DATA_DIR 覆盖），开发为项目根。"""
    env = os.environ.get("BIDMASTER_DATA_DIR")
    if env:
        return Path(env)
    if is_frozen():
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "laoma-bid"
    return _project_root()


def ensure_data_root() -> Path:
    """确保数据目录及标准子目录存在，返回 data_root。"""
    root = data_root()
    root.mkdir(parents=True, exist_ok=True)
    # 打包后 data/ 等相对路径目录不会自动存在，统一创建（relative 解析基于启动后的 cwd）
    for sub in ("data", "projects", "uploads", "chroma_db", "static/output"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def copy_bundled_resources() -> None:
    """把打包的只读资源（static/templates/skills）同步到可写数据目录。

    版本比对策略：
    - 数据目录的 .bundle_stamp 与当前应用版本标识一致 → 跳过（日常启动零覆盖，
      用户对模板/技能的自定义修改不会被抹掉）
    - 不一致（首次运行或应用升级）→ 全量同步一次并更新 stamp
    - 开发模式（src == dst）为空操作
    """
    src = app_root()
    dst = data_root()
    if src == dst:
        return  # 开发模式：无需复制

    # 版本标识：frozen 用 exe 文件的 mtime+size（每次构建必变）；其他用 _MEIPASS 路径
    exe = Path(sys.executable) if is_frozen() else None
    if exe and exe.is_file():
        st = exe.stat()
        current_stamp = f"{int(st.st_mtime)}-{st.st_size}"
    else:
        current_stamp = f"meipass-{int(Path(app_root()).stat().st_mtime)}"

    stamp_file = dst / ".bundle_stamp"
    if stamp_file.is_file():
        try:
            if stamp_file.read_text(encoding="utf-8").strip() == current_stamp:
                return  # 同一版本已同步过
        except OSError:
            pass

    for name in ("static", "templates", "skills"):
        s = src / name
        if s.is_dir():
            d = dst / name
            d.mkdir(parents=True, exist_ok=True)
            for f in s.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(s)
                    target = d / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(f.read_bytes())

    try:
        stamp_file.write_text(current_stamp, encoding="utf-8")
    except OSError:
        pass
