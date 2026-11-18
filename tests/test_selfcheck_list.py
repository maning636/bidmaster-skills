"""selfcheck_list 技能冒烟测试（不依赖真实标书文件、不调 LLM）。"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext, SkillResult
from skills.selfcheck_list import SelfcheckListSkill


def test_skill_metadata():
    """可实例化，且 name / category 非空。"""
    skill = SelfcheckListSkill()
    assert skill.name == "selfcheck_list"
    assert skill.category == "check"
    assert skill.name
    assert skill.category


def test_execute_with_minimal_input():
    """最小构造 check_results 跑 execute，返回 SkillResult 且 success 为 True。"""
    skill = SelfcheckListSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={
            "check_results": {
                "pricing_check": {"has_critical_issues": False, "risk_level": "low",
                                  "summary": {"failed": 0}},
                "qualification_check": {"has_critical_issues": True, "risk_level": "high",
                                        "summary": {"failed": 2}},
            }
        },
    )
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    assert "categories" in result.data
    assert result.data["total_items"] == 20
    assert result.data["passed_items"] == 3  # pricing_check 通过 → SC-14/15/16 为 pass


def test_execute_empty_input_all_pending():
    """空 check_results：全部条目 pending，can_submit 为 False，仍返回 success。"""
    skill = SelfcheckListSkill()
    ctx = SkillContext(project_id="demo", db=None, llm=None, parameters={"check_results": {}})
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    assert result.data["total_items"] == 20
    assert result.data["passed_items"] == 0
    assert result.data["can_submit"] is False
