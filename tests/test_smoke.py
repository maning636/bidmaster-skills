"""最小冒烟：引擎能加载示例技能并执行；排版技能可导入；JSON 修复可用。"""
from __future__ import annotations

import asyncio
from pathlib import Path

from skill_engine.base import SkillContext
from skill_engine.loader import SkillLoader
from skill_engine.registry import SkillRegistry
from utils.json_repair import JsonRepairEngine

ROOT = Path(__file__).resolve().parent.parent


def test_example_skill_runs():
    loader = SkillLoader(ROOT / "examples")
    loaded = loader.load_all()
    assert loaded, "示例技能未被发现（布局应为 <root>/<category>/<skill>/SKILL.md）"
    for key in loaded:
        SkillRegistry.instance().register(loader.get_skill_class(key))
    cls = SkillRegistry.instance().get("hello_skill")
    ctx = SkillContext(project_id="demo", db=None, llm=None, parameters={"text": "hi"})
    result = asyncio.run(cls().execute(ctx))
    assert result.success and result.data["upper"] == "HI"


def test_docx_format_importable():
    from skills.docx_format import DocxFormatSkill

    assert DocxFormatSkill.name == "docx_format"


def test_json_repair_handles_common_breakage():
    engine = JsonRepairEngine()
    assert asyncio.run(engine.repair_and_validate('{"a": 1, "b": [1,2,], }')) == {"a": 1, "b": [1, 2]}
    assert engine.extract_json('```json\n{"x": "y"}\n```').strip() == '{"x": "y"}'
