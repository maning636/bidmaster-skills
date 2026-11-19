"""selfcheck_list 技能的行为契约测试。

核心是「自检清单生成」：按固定清单模板 + 已有检查结果，算出哪些项通过。
验证重点：
- 清单条目数与分类固定（模板不能被意外改小）
- 已有检查结果能正确点亮对应项
- 全部通过时 can_submit=True，有失败项时 False
"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext
from skills.selfcheck_list import SelfcheckListSkill


def _run(check_results: dict | None = None):
    ctx = SkillContext(project_id="t", db=None, llm=None,
                       parameters={"check_results": check_results or {}})
    return asyncio.run(SelfcheckListSkill().execute(ctx))


def test_skill_metadata():
    s = SelfcheckListSkill()
    assert s.name == "selfcheck_list"
    assert s.category == "check"


def test_output_schema():
    r = _run()
    assert r.success is True
    assert set(r.data) >= {"categories", "all_passed", "can_submit",
                           "total_items", "passed_items"}


def test_total_items_matches_flat_count():
    """total_items 必须等于所有分类下条目数之和。"""
    r = _run()
    flat = sum(len(c["items"]) for c in r.data["categories"])
    assert r.data["total_items"] == flat
    assert flat > 0, "清单模板不该是空的"


def test_empty_check_results_all_pending():
    """没有任何检查结果时，所有项应为 pending，passed_items 为 0。"""
    r = _run({})
    assert r.data["passed_items"] == 0
    assert r.data["all_passed"] is False
    assert r.data["can_submit"] is False
    for cat in r.data["categories"]:
        for item in cat["items"]:
            assert item["status"] in ("pending", "fail", "warning")


def test_each_item_has_required_fields():
    r = _run()
    for cat in r.data["categories"]:
        assert cat.get("category")
        for item in cat["items"]:
            assert set(item) >= {"id", "content", "status"}
            assert item["id"], "条目必须有稳定 id，供前端回填"
            assert item["content"], "条目必须有可读文案"


def test_item_ids_are_unique():
    """id 重复会让前端回填错位。"""
    r = _run()
    ids = [item["id"] for cat in r.data["categories"] for item in cat["items"]]
    assert len(ids) == len(set(ids)), f"存在重复 id：{len(ids)} vs {len(set(ids))}"


def test_passed_items_never_exceeds_total():
    r = _run({"qualification_check": {"passed": True}})
    assert 0 <= r.data["passed_items"] <= r.data["total_items"]


def test_can_submit_implies_all_passed():
    """can_submit 与 all_passed 必须一致 —— 不能出现「没全过却能提交」。"""
    r = _run()
    assert r.data["can_submit"] == r.data["all_passed"]
