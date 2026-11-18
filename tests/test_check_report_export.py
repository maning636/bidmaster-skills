"""check_report_export 技能冒烟测试（不依赖真实标书文件、不调 LLM）。"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext, SkillResult
from skills.check_report_export import CheckReportExportSkill


def test_skill_metadata():
    """可实例化，且 name / category 非空。"""
    skill = CheckReportExportSkill()
    assert skill.name == "check_report_export"
    assert skill.category == "check"
    assert skill.name
    assert skill.category


def test_execute_with_minimal_input():
    """用最小构造输入跑 execute，返回 SkillResult 且 success 为 True。"""
    skill = CheckReportExportSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={
            "report_data": {
                "checks": [
                    {"check_type": "price_limit", "status": "pass", "detail": "ok"},
                ],
                "summary": {"total": 1, "passed": 1, "failed": 0, "warning": 0},
                "risk_level": "low",
            },
            "format": "markdown",
            "project_name": "测试项目",
        },
    )
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    assert "content" in result.data
    assert "format" in result.data
    assert result.data["format"] == "markdown"
    assert "投标文件检查报告" in result.data["content"]


def test_execute_empty_report_fails():
    """空 report_data 应返回 success=False 而非抛异常。"""
    skill = CheckReportExportSkill()
    ctx = SkillContext(project_id="demo", db=None, llm=None, parameters={})
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is False
