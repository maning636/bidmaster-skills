# check_report_export · 检查报告导出

把检查结果数据渲染成 Markdown / HTML / JSON 正文。纯字符串处理，不调用大模型，不读写文件，不依赖数据库。

## Agent 什么时候该调用我

**该调用：**

- 你手上已有多个技能的结构化结果（`checks` 数组），要生成一份可交付报告
- 用户要「导出报告」「给我一份检查结果」
- 需要 Markdown / HTML / 纯文本三种格式之一

**不该调用：**

- 你手上还没有检查结果 → 先跑对应检查技能
- 用户要「总结一下问题」→ 你自己组织语言更好，本技能只是模板填充

**定位：** 这是「格式化输出」工具，不做分析。它把
`{checks, summary, risk_level}` 渲染成人类能读的报告。

## 输入

`execute` 只读 `ctx.parameters`，全部可选：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `report_data` | dict | 否 | 检查结果数据；需含 `checks`（list[dict]），可选 `summary` / `risk_level` 及其他字段。空 dict 或缺失 → `success=False` |
| `format` | str | 否 | 导出格式：`"markdown"`（默认）| `"html"` | `"json"`；未知格式回退为 Markdown |
| `project_name` | str | 否 | 报告标题中的项目名，默认 `"未命名项目"` |

## 输出

`SkillResult`：

- `report_data` 为空时：`success=False`，`error="无报告数据"`。
- 否则 `success=True`，`data` 结构：

```json
{
  "content": "……报告正文……",
  "format": "markdown|html|json",
  "size": 1234,
  "generated_at": "2026-11-18T14:00:00"
}
```

`content` 是渲染后的正文（Markdown / HTML / JSON 文本），`size` 为 UTF-8 字节数，`generated_at` 为 ISO 时间戳。

## 渲染要点

- `checks` 为 list 时输出：标题块 → 检查概要（风险等级 + 计数）→ 详细检查结果表格 → 不通过项详情。
- `checks` 非 list 时把 `checks`/`summary`/`risk_level`/`has_critical_issues` 之外的字段按 JSON 原样内嵌。
- HTML 由 Markdown 逐行转换（标题 / 列表 / 表格 / 分隔线 / 段落），内联样式。

## 属性

- `name = "check_report_export"`，`category = "check"`，`version = "1.0.0"`
- `triggers = ["导出报告", "报告导出", "检查报告"]`
