"""risk_score 技能冒烟测试（不依赖真实标书文件、不调 LLM）。"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext, SkillResult
from skills.risk_score import RiskScoreSkill


def test_skill_metadata():
    """可实例化，且 name / category 非空。"""
    skill = RiskScoreSkill()
    assert skill.name == "risk_score"
    assert skill.category == "check"
    assert skill.name
    assert skill.category


def test_execute_with_minimal_input():
    """最小构造 check_results 跑 execute，返回 SkillResult 且 success 为 True。"""
    skill = RiskScoreSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={
            "check_results": {
                "field_overlap": {"checks": [{"status": "fail"}]},
                "price": {"checks": [{"status": "fail"}]},
                "metadata": {"anomalies": [{"x": 1}]},
                "structure": {"missing_sections": ["章1"]},
                "text": {"issues": [{"severity": "high"}]},
                "rare_sequences": {"rare_sequences": [{"x": 1}]},
            }
        },
    )
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    assert "composite_score" in result.data
    assert "risk_level" in result.data
    assert len(result.data["dimensions"]) == 6


def test_execute_empty_input_graceful():
    """空 check_results：应优雅返回失败。"""
    skill = RiskScoreSkill()
    ctx = SkillContext(project_id="demo", db=None, llm=None, parameters={"check_results": {}})
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is False
    assert result.error
