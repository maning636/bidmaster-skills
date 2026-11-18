# risk_score · 风险评分

对上游六类检查结果做加权综合评分，用于投标风险分级。纯规则判定，不调用大模型，
不依赖数据库。

## 输入

`execute` 只读 `ctx.parameters["check_results"]`，形如：

```json
{
  "field_overlap":   {"checks": [...], "score": 30, "anomalies": [...]},
  "price":           {"checks": [...], "score": 50},
  "metadata":        {"anomalies": [...], "score": 20},
  "structure":       {"missing_sections": [...], "score": 10},
  "text":            {"issues": [...], "score": 10},
  "rare_sequences":  {"rare_sequences": [...], "score": 5}
}
```

为空时返回失败。

## 输出

`SkillResult.success = True`，`data` 结构：

```json
{
  "composite_score": 42.5,
  "risk_level": "high|medium|low",
  "dimensions": {
    "field_overlap": {"score": 0.0, "weight": 0.2, "weighted_score": 0.0,
                      "description": "...", "detail": "..."}
  },
  "summary": {"highest_risk": "...", "lowest_risk": "...",
              "critical_dimensions": ["..."]},
  "recommendations": ["..."]
}
```

## 评分规则

| 维度 | 权重 | 计分 |
|---|---|---|
| `field_overlap` | 0.20 | 失败项占比 |
| `price` | 0.20 | 失败×2 + warning，按 50 分制换算 |
| `metadata` | 0.15 | 异常数 ×25 |
| `structure` | 0.15 | 缺失章节数 ×15 |
| `text` | 0.20 | high×20 + medium×8 + low×3 |
| `rare_sequences` | 0.10 | 异常序列数 ×30 |

综合得分 ≥70 → `high`；≥40 → `medium`；否则 `low`。任一维度 ≥70 进入
`summary.critical_dimensions` 并在 `recommendations` 中列出整改提示。

## 属性

- `name = "risk_score"`，`category = "check"`，`version = "1.0.0"`
- `triggers = ["风险评分", "风险打分", "综合风险"]`
