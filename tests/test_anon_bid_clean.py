"""anon_bid_clean 技能冒烟测试（不依赖真实标书文件、不调 LLM）。"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext, SkillResult
from skills.anon_bid_clean import AnonBidCleanSkill


def test_skill_metadata():
    """可实例化，且 name / category 非空。"""
    skill = AnonBidCleanSkill()
    assert skill.name == "anon_bid_clean"
    assert skill.category == "check"
    assert skill.name
    assert skill.category


def test_execute_text_mode_minimal_input():
    """文本降级模式：传入 bid_text + company_names，无需真实 .docx 即可跑 execute。"""
    skill = AnonBidCleanSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={
            "bid_text": "公司资质说明：老马科技股份有限公司成立于2010年。\n常规无身份信息段落。",
            "company_names": ["老马科技股份有限公司"],
        },
    )
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    assert result.data["mode"] == "text"
    assert result.data["issues"], "文本模式应能检出 company_name 残留"


def test_execute_empty_params_graceful():
    """空参数：应优雅返回失败而非抛异常。"""
    skill = AnonBidCleanSkill()
    ctx = SkillContext(project_id="demo", db=None, llm=None, parameters={})
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is False
    assert result.error
