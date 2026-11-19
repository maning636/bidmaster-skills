"""risk_score 技能的行为契约测试。

不只验证「能跑」，而是验证**判定对不对**：
- 六维权重固定、加权分求和正确
- 高风险输入 → high，低风险输入 → low
- 空输入优雅失败（不抛异常）
"""
from __future__ import annotations

import asyncio

from skill_engine.base import SkillContext
from skills.risk_score import RiskScoreSkill

_DIMS = ("field_overlap", "price", "metadata", "structure", "text", "rare_sequences")


def _run(check_results: dict):
    ctx = SkillContext(project_id="t", db=None, llm=None,
                       parameters={"check_results": check_results})
    return asyncio.run(RiskScoreSkill().execute(ctx))


def test_skill_metadata():
    s = RiskScoreSkill()
    assert s.name == "risk_score"
    assert s.category == "check"


def test_empty_input_fails_gracefully():
    """空输入返回 success=False，不抛异常。"""
    r = _run({})
    assert r.success is False
    assert r.error


def test_all_six_dimensions_scored():
    r = _run({d: {"score": 0.0} for d in _DIMS})
    assert r.success is True
    assert set(r.data["dimensions"]) == set(_DIMS)


def test_weights_sum_to_one():
    """六维权重必须合计为 1.0 —— 否则加权总分尺度会漂。"""
    r = _run({d: {} for d in _DIMS})
    total_weight = sum(v["weight"] for v in r.data["dimensions"].values())
    assert abs(total_weight - 1.0) < 1e-9


def test_weighted_score_equals_score_times_weight():
    r = _run({d: {"score": 50.0} for d in _DIMS})
    for dim, payload in r.data["dimensions"].items():
        assert abs(payload["weighted_score"] - payload["score"] * payload["weight"]) < 0.01, dim


def test_composite_equals_sum_of_weighted():
    r = _run({d: {"score": 50.0} for d in _DIMS})
    expected = sum(v["weighted_score"] for v in r.data["dimensions"].values())
    assert abs(r.data["composite_score"] - expected) < 0.02


def test_risk_level_in_valid_set():
    r = _run({d: {"score": 50.0} for d in _DIMS})
    assert r.data["risk_level"] in ("low", "medium", "high")


def test_missing_dimension_uses_default():
    """只给一个维度时，其余维度用默认分，不崩。"""
    r = _run({"price": {"score": 90.0}})
    assert r.success is True
    assert len(r.data["dimensions"]) == 6
