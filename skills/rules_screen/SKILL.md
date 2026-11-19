# rules_screen · 法规规则筛查

按规则库 `data/rules/rules_v1.json` 的关键词对招标/投标文本做筛查，分级报告命中法规条款 / 提示性匹配 / 已核验通过。纯规则判定，不调用大模型，不依赖数据库。

## Agent 什么时候该调用我

**该调用：**

- 用户给了一份规则包（JSON），要按规则筛内容
- 用户问「这段话违反了哪条法规」「有没有踩红线」
- 需要批量匹配规则并给出命中位置

**不该调用：**

- 用户没有规则包 → 先用你自己的知识回答，或建议他准备规则包
- 用户问「这条法规什么意思」→ 这是解释，你自己答
- 需要「理解」条款的隐含意图 → 你自己判断，本技能只做字面匹配

**为什么交给代码：** 规则包可能上百条，逐条比对是穷尽扫描。
大模型既读不全规则，也会漏掉命中项。

## 输入

`execute` 只读 `ctx.parameters`，全部可选：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `tender_text` | str | 否 | 招标文件文本 |
| `bid_text` | str | 否 | 投标文件文本（以 bid 为主、tender 为辅拼接） |

两者都为空时返回 `success=False`。

## 输出

`SkillResult.success = True`，`data` 结构：

```json
{
  "items": [
    {"rule_id": "R-1001", "title": "...", "status": "hit|note|clear",
     "evidence_level": "verdict|hint", "basis": "...", "checked": true,
     "source_url": "...", "matched_keyword": "..."}
  ],
  "summary": {"hit": 0, "note": 0, "clear": 0, "total": 0},
  "rules_path": "/abs/path/to/rules_v1.json",
  "risk_level": "high|low",
  "evidence_summary": {"total": 0, "checked": 0, "unchecked": 0, "verdict": 0, "hint": 0}
}
```

- `status = "hit"`：verdict 规则命中关键词 → 报告命中法规条款
- `status = "note"`：hint 规则命中（提示性，需人工判断）
- `status = "clear"`：verdict 规则未命中 → 已核验通过
- 规则未配置关键词 → `status = "note"`、`checked = false`
- hint 规则未命中 → 不产出结果条目

## 依赖的规则包格式

规则包为 JSON，顶层结构：

```json
{
  "version": "v1",
  "generated_at": "...",
  "rules": [
    {"rule_id": "R-1001", "title": "投标函", "legal_level": "verdict|hint",
     "category": "...", "check_hint": "...", "source_url": "..."}
  ]
}
```

路径解析顺序：环境变量 `BMP_RULES_JSON_PATH` → `data_root()/data/rules/rules_v1.json` → `app_root()/data/rules/rules_v1.json`。文件缺失或 JSON 非法时 `execute` 返回 `success=False`（不抛异常）。

`verdict` 规则使用本技能内置的 `RULE_KEYWORDS` 手工关键词；其余规则从 `title` + `check_hint` 切出 ≥2 字中文词组作为关键词。

## 属性

- `name = "rules_screen"`，`category = "check"`，`version = "1.0.0"`
- `triggers = ["法规筛查", "规则筛查", "关键词筛查", "条款筛查"]`
