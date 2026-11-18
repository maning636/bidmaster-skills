"""self_score 技能冒烟测试（不依赖真实标书文件、不调 LLM）。"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext, SkillResult
from skills.self_score import SelfScoreSkill


def test_skill_metadata():
    """可实例化，且 name / category 非空。"""
    skill = SelfScoreSkill()
    assert skill.name == "self_score"
    assert skill.category == "check"
    assert skill.name
    assert skill.category


def test_execute_with_minimal_input():
    """最小构造 scoring_rows / blocks 跑 execute，返回 SkillResult 且 success 为 True。"""
    skill = SelfScoreSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={
            "scoring_rows": [
                {"item": "技术方案", "category": "技术", "score": 40},
                {"item": "商务报价", "category": "商务", "score": 30},
            ],
            "blocks": [
                {"title": "技术方案", "score_items": ["技术方案"], "content_length": 600},
                {"title": "商务报价", "score_items": ["商务报价"], "content_length": 0},
            ],
        },
    )
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    assert "total_max" in result.data
    assert "items" in result.data
    assert len(result.data["items"]) == 2
    assert result.data["total_max"] == 70.0


def test_execute_empty_input_graceful():
    """空 scoring_rows：应优雅返回失败。"""
    skill = SelfScoreSkill()
    ctx = SkillContext(project_id="demo", db=None, llm=None, parameters={"scoring_rows": []})
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is False
    assert result.error
