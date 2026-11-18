# docx_format · Word 智能排版

对 `.docx` 做格式检查、排版、差异对比与美化。四种模式共用一个入口，靠 `mode` 参数切换。

## 属性

| 项 | 值 |
|---|---|
| `name` | `docx_format` |
| `category` | `output` |
| 依赖 | `python-docx` |

## 输入（`SkillContext.parameters`）

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `file_path` | `str` | 是 | — | 目标 `.docx` 的绝对路径 |
| `mode` | `str` | 否 | `format` | `format` / `check` / `diff` / `beautify` |
| `config` | `dict` | 否 | `{}` | 覆盖默认排版配置，见下方「配置项」 |

## 输出（`SkillResult`）

文件不存在或打不开时返回 `success=False` + `error`。

### `mode=format`

```json
{
  "output_path": "…/xxx_formatted.docx",
  "stats": {
    "paragraphs": 739,
    "headings": 121,
    "body": 618,
    "tables": 27,
    "margins_fixed": 4
  }
}
```

### `mode=check`

```json
{
  "total_paragraphs": 739,
  "checked_runs": 2149,
  "total_issues": 1218,
  "font_issues": 402,
  "size_issues": 388,
  "indent_issues": 350,
  "margin_issues": 78,
  "issues": [ { "type": "font_mismatch", "…": "…" } ],
  "compliance_rate": 43.3
}
```

`issues` 最多返回前 100 条；`compliance_rate` 为百分比（保留 1 位）。

### `mode=diff` / `mode=beautify`

返回对应的差异清单 / 美化结果，schema 与 `check` 同族。

## 配置项（`config`，全部可选）

| 键 | 说明 |
|---|---|
| `heading_number_format` | 标题编号格式：`decimal` / `decimal_paren` / `chinese_paren` / `mixed` / `letter` / `chinese` |
| `enable_table_formatting` | 是否处理表格边框，默认 `true` |
| `page_number_font` | 页脚页码字体，默认 `宋体` |
| 其余 | 见源码 `DEFAULT_FORMAT_CONFIG` |

## 行为说明

- **标题识别**：按点分隔十进制编号的段数推断层级（`1.` → 2 级，`1.1.` → 3 级，最深 8 级），逐条正则从深到浅匹配，命中即得层级。
- **运行时配置生效**：标题识别读的是运行时 `config`，不是模块级默认值 —— 这是修过的 bug，改动时别退回去。
- **线程隔离**：`python-docx` 的段落遍历与 `doc.save` 是同步 IO/CPU，长文档秒级，全部走 `asyncio.to_thread`，不阻塞事件循环。
- **输出文件名**：`format` 模式产出 `原文件名_formatted.docx`，不覆盖原文件。

## 示例

```python
from skill_engine.base import SkillContext
from skills.docx_format import DocxFormatSkill

ctx = SkillContext(
    project_id="demo",
    db=None,
    llm=None,
    parameters={
        "file_path": "D:/path/to/招标文件.docx",
        "mode": "check",
    },
)
result = await DocxFormatSkill().execute(ctx)
print(result.data["total_issues"])
```
