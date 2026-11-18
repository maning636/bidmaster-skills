"""rules_screen 技能测试（不依赖真实标书文件、不调 LLM）。"""
from __future__ import annotations

import asyncio
import json

from skill_engine.base import SkillContext, SkillResult
from skills.rules_screen import RulesScreenSkill


def test_skill_metadata():
    """可实例化，且 name / category 非空。"""
    skill = RulesScreenSkill()
    assert skill.name == "rules_screen"
    assert skill.category == "check"
    assert skill.name
    assert skill.category


def test_execute_missing_rules_returns_gracefully(monkeypatch):
    """规则包文件缺失时 execute 优雅返回（不抛异常）。

    把环境变量覆盖指向一个不存在的路径，确保定位到缺失文件。
    """
    skill = RulesScreenSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={"bid_text": "投标函：投标报价 100 万元"},
    )
    # 覆盖为不存在路径，避免受仓库内真实规则包影响
    monkeypatch.setenv("BMP_RULES_JSON_PATH", "/nonexistent/rules_v1.json")
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is False
    assert "规则包文件不存在" in (result.error or "")


def test_execute_with_minimal_rules_package(tmp_path, monkeypatch):
    """用 tmp_path 造一个最小规则包 JSON，让 execute 真跑一次。"""
    rules_pkg = {
        "version": "v1",
        "generated_at": "2026-01-01T00:00:00",
        "rules": [
            {
                "rule_id": "R-1001",
                "title": "投标函",
                "legal_level": "verdict",
                "check_hint": "投标函必须载明投标报价",
                "source_url": "https://example.com/rule/1001",
            },
        ],
    }
    pkg_path = tmp_path / "rules_v1.json"
    pkg_path.write_text(json.dumps(rules_pkg, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("BMP_RULES_JSON_PATH", str(pkg_path))

    skill = RulesScreenSkill()
    ctx = SkillContext(
        project_id="demo",
        db=None,
        llm=None,
        parameters={"bid_text": "投标函：投标报价 100 万元"},
    )
    result = asyncio.run(skill.execute(ctx))
    assert isinstance(result, SkillResult)
    assert result.success is True
    assert "items" in result.data
    assert "summary" in result.data
    # 关键词 "投标报价" 命中 → verdict 规则出 hit
    assert result.data["summary"]["hit"] == 1
    assert result.data["items"][0]["status"] == "hit"
