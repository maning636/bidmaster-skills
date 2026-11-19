"""check_report_export 技能的行为契约测试。

把检查结果 dict 渲染成可交付的报告（markdown / html / text）。
验证重点：
- 三种格式都能产出非空内容
- 失败项必须出现在报告里（否则报告没意义）
- 空数据优雅处理
"""
from __future__ import annotations

import asyncio

import pytest

from skill_engine.base import SkillContext
from skills.check_report_export import CheckReportExportSkill

_REPORT = {
    "checks": [
        {"check_type": "price_limit", "status": "fail", "detail": "投标总价超过最高限价"},
        {"check_type": "arithmetic", "status": "pass", "detail": "算术验算通过"},
    ],
    "summary": {"total": 2, "passed": 1, "failed": 1, "warning": 0},
    "risk_level": "high",
}


def _run(report_data: dict | None = None, fmt: str = "markdown"):
    ctx = SkillContext(project_id="t", db=None, llm=None,
                       parameters={
                           "report_data": report_data if report_data is not None else _REPORT,
                           "format": fmt,
                           "project_name": "测试项目",
                       })
    return asyncio.run(CheckReportExportSkill().execute(ctx))


def test_skill_metadata():
    s = CheckReportExportSkill()
    assert s.name == "check_report_export"
    assert s.category == "check"


def test_output_schema():
    r = _run()
    assert r.success is True
    assert set(r.data) >= {"content", "format", "size", "generated_at"}
    assert isinstance(r.data["content"], str)
    assert r.data["content"], "报告内容不能为空"


@pytest.mark.parametrize("fmt", ["markdown", "html", "text"])
def test_all_formats_produce_content(fmt):
    r = _run(fmt=fmt)
    assert r.success is True, r.error
    assert len(r.data["content"]) > 20


def test_size_is_utf8_byte_length():
    """size 是 UTF-8 字节数（不是字符数）—— 中文报告按字节算才准确。"""
    r = _run()
    assert r.data["size"] == len(r.data["content"].encode("utf-8"))
    assert r.data["size"] > len(r.data["content"]), "中文内容字节数应大于字符数"


def test_failed_item_appears_in_report():
    """失败项必须出现在报告里 —— 报告漏掉失败项等于骗人。"""
    r = _run()
    assert "超过最高限价" in r.data["content"]


def test_project_name_appears():
    r = _run()
    assert "测试项目" in r.data["content"]


def test_empty_report_does_not_crash():
    r = _run({"checks": [], "summary": {}, "risk_level": "low"})
    assert r.success is True
    assert isinstance(r.data["content"], str)


def test_format_defaults_to_markdown_when_omitted():
    ctx = SkillContext(project_id="t", db=None, llm=None,
                       parameters={"report_data": _REPORT})
    r = asyncio.run(CheckReportExportSkill().execute(ctx))
    assert r.success is True
    assert r.data["format"] == "markdown"
