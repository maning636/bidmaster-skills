# selfcheck_list · 废标自查清单

读取一批下游 check skill 的原始输出，按预置的 SC 编号检查项逐条折算成
`pass / fail / pending` 三态，最后聚合出投标文件能不能提交的结论。纯规则判定，
不调用大模型，不依赖数据库。

## Agent 什么时候该调用我

**该调用：**

- 用户问「提交前还要准备什么」「有没有漏的」
- 需要一份「已完成/未完成」的清单给用户核对
- 出件前的最后一道自检

**不该调用：**

- 还没有任何检查结果 → 先跑检查技能，本技能靠结果点亮条目
- 用户问「这条要求是什么意思」→ 你自己解释

**输出特点：** 返回固定清单模板（按分类组织），每条带 `status`。
`can_submit` 为 `True` 时才可以提交 —— 这个判断是硬规则，不靠感觉。

## 输入

`execute` 只读 `ctx.parameters["check_results"]`，形如：

```json
{
  "qualification_check": {"has_critical_issues": false, "risk_level": "low", "summary": {"failed": 0}},
  "pricing_check":       {"has_critical_issues": false, "risk_level": "low", "summary": {"failed": 0}}
}
```

键与内置 `SELFCHECK_ITEMS` 里各条的 `check_skill` 对齐；缺失的键对应条目为
`pending`。

## 输出

`SkillResult.success = True`，`data` 结构：

```json
{
  "categories": [
    {"category": "资质文件核查",
     "items": [{"id": "SC-01", "content": "...", "status": "pass|fail|pending",
                "check_skill": "qualification_check"}]}
  ],
  "all_passed": true,
  "can_submit": true,
  "total_items": 20,
  "passed_items": 20
}
```

## 检查项

内置 `SELFCHECK_ITEMS` 共 5 大类、20 条（SC-01 ~ SC-20）：资质文件核查、投标保证金核查、
文件完整性与签章核查、技术与报价核查、有效期与合规核查。**业务数据不可删减**：SC 编号、
归属的 `check_skill` 及判定含义必须保持稳定；扩展只允许追加，不得重排或删除。

## 判定规则

下游输出为空对象、`has_critical_issues` 为真、`risk_level` 落在 `high`/`critical`、
或 `summary.failed > 0` → `fail`；其余 → `pass`。

## 属性

- `name = "selfcheck_list"`，`category = "check"`，`version = "1.0.0"`
- `triggers = ["自查", "废标自查", "提交前检查"]`
