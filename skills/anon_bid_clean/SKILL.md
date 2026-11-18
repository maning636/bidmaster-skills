# anon_bid_clean · 暗标清洗检查

扫描投标文件（`.docx`）中残留的身份信息，避免因作者名、公司名、页眉页脚 Logo
或文档属性等残留信息导致直接废标。纯规则判定，不调用大模型，不依赖数据库；
依赖 `python-docx`。

## 输入

`execute` 只读 `ctx.parameters`：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file_path` | str | 否 | `.docx` 文件路径（推荐，完整四类检查）。与 `bid_file_path` 二选一 |
| `bid_file_path` | str | 否 | `file_path` 的别名 |
| `bid_text` | str | 否 | 降级模式：无 `file_path` 但有 `bid_text` 时仅做正文公司名扫描 |
| `company_names` | list[str] | 否 | 正文公司名残留扫描用的公司全称/简称列表 |

必须提供 `file_path`（存在且为 `.docx`）**或** `bid_text`，否则返回失败。

## 输出

`SkillResult.success = True`，`data` 结构：

```json
{
  "skill_name": "anon_bid_clean",
  "check_type": "disqualification",
  "mode": "file|text",
  "passed": true,
  "issues": [
    {"severity": "critical|warning", "category": "metadata|logo|company_name",
     "message": "...", "location": "...", "suggestion": "..."}
  ],
  "summary": "..."
}
```

`issues` 为空表示未检测到身份信息残留；`passed` 为 `False` 当存在 `critical`
级问题时。`warnings` 在存在高危项时给出提示。

## 检查项（文件模式）

1. **文档属性元数据**（`core_properties`）：作者、最后修改人、公司、标题。
2. **页眉/页脚 Logo**：XML 层 `w:drawing`/`w:pict` + 关系层 `image/*` 双重计数。
3. **正文公司名残留**：需要传入 `company_names`；未提供时产生一条 warning 并跳过。
4. **docProps XML**（`app.xml` / `core.xml` 原始字段）。

文本降级模式（仅 `bid_text`）只能做正文公司名扫描，其余三类不可用。

## 属性

- `name = "anon_bid_clean"`，`category = "check"`，`version = "1.0.0"`
- `triggers = ["暗标", "匿名评标", "匿名投标", "公司名残留", "Logo残留", "元数据清洗", "身份信息"]`
