"""pricing_check 技能冒烟测试（不依赖真实标书文件、不调 LLM）。"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext, SkillResult
from skills.pricing_check import PricingCheckSkill


def test_skill_metadata():
    """可实例化，且 name / category 非空。"""
    skill = PricingCheckSkill()
    assert skill.name == "pricing_check"
    assert skill.category == "check"
    assert skill.name
    assert skill.category


def test_execute_with_minimal_input():
    """用最小构造输入跑 execute，返回 SkillResult 且 success 为 True。"""
    skill = PricingCheckSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={
            "bid_text": "投标总价：98.5万\n1. 单价 12.34 × 数量 5 = 61.70\n总金额：壹万元（10000）",
            "max_price": 100.0,
        },
    )
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    # data schema：{checks, summary, risk_level}
    assert "checks" in result.data
    assert "summary" in result.data
    assert "risk_level" in result.data
    assert len(result.data["checks"]) == 4
