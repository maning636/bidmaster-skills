# bidmaster-skills

**投标文档处理的技能集**：技能引擎 + Word 排版 + 大模型坏 JSON 修复。从「老马标书贤内助」抽出的开源子集，可独立 `pip install` 使用，也可作为你自己产品的技能底座。

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-pytest-informational)](tests/)

> 如果这个库帮你省了时间，**点个 Star** 就是最好的支持 —— 也方便你下次找到它。

---

## 这个库解决什么问题

做招投标 / 投标文件（标书）自动化时，有三件脏活没人愿意重写：

| 脏活 | 本库的方案 |
|---|---|
| Word 排版不可控：字体、字号、缩进、行距、页码，人工抄格式必出错 | `skills/docx_format`：四种模式（排版 / 格式检查 / 与模板对比 / XML 美化），可量化报告「哪一段字体不对」 |
| 大模型返回的 JSON 十次有一次是坏的（尾逗号、裸键、被 `<think>` 包裹） | `utils/json_repair`：多候选修复 + 逐级降级，不抛异常 |
| 技能散落各处、注册靠手写 import | `skill_engine`：按 `SKILL.md` 目录布局自动发现、注册、按分类查询 |

## 快速开始

```bash
pip install -e .
```

### 1. 跑一个技能

```python
import asyncio
from skill_engine.loader import SkillLoader
from skill_engine.registry import SkillRegistry
from skill_engine.base import SkillContext

loader = SkillLoader("examples")   # 布局：<root>/<category>/<skill>/SKILL.md
meta = loader.load_all()
for key in meta:
    SkillRegistry.instance().register(loader.get_skill_class(key))

skill = SkillRegistry.instance().get("hello_skill")()
result = asyncio.run(skill.execute(SkillContext(project_id="demo", db=None, llm=None,
                                                parameters={"text": "hello"})))
print(result.data)   # {'upper': 'HELLO'}
```

### 2. Word 排版

```python
import asyncio
from skills.docx_format import DocxFormatSkill
from skill_engine.base import SkillContext

skill = DocxFormatSkill()
res = asyncio.run(skill.execute(SkillContext(
    project_id="demo", db=None, llm=None,
    parameters={"file_path": "your.docx", "mode": "check"},
)))
print(res.data["total_issues"])   # 1218（真实标书实测：739 段 / 2149 run / 1218 处问题）
```

`mode` 支持 `format`（排版）/ `check`（检查）/ `diff`（与模板对比）/ `beautify`（XML 美化）。

### 3. 修复坏 JSON

```python
from utils.json_repair import repair_json
print(repair_json('{"a": 1, "b": [1,2,], }'))   # {'a': 1, 'b': [1, 2]}
```

## 目录结构

```
skill_engine/        # 技能发现 / 注册 / 执行契约
  base.py            # Skill 基类、SkillContext、SkillResult、进度回调
  loader.py          # 按 <root>/<category>/<skill>/SKILL.md 扫描
  registry.py        # 技能注册表（按名字/分类查询）
skills/docx_format/  # Word 排版技能（947 行）
utils/json_repair.py # 大模型坏 JSON 修复（335 行）
examples/            # 最小示例技能
tests/               # 冒烟与回归
```

## 加入社群

- 微信群 / 公众号：`docs/community.md`（含二维码）
- 官网：<https://example.com/?utm_source=github&utm_medium=readme&utm_campaign=bidmaster-skills>
- 问题反馈：GitHub Issues；商业合作与私有知识库能力见官网

## 关键词

招投标 · 标书 · 投标文件 · 合规检查 · Word 排版 · docx · 格式检查 · 大模型结构化输出 · biddding · tender · RFP · skill-engine · LLM JSON repair

## 许可

**AGPL-3.0**。全文见 `LICENSE`。

本库的 `skill_engine/`、`skills/docx_format/` 与 `utils/json_repair.py` **派生自 AGPL-3.0 上游项目** [BidMaster-Pro](https://github.com/guangshu100/BidMaster-Pro)（经由「老马标书贤内助」主仓），因此本仓库整体必须保持 AGPL-3.0，**不得改为 MIT 或其他更宽松许可**。上游归属与实测相似度见 `NOTICE`。

本库是「老马标书贤内助」的开源子集：只包含**不依赖大模型**的通用引擎与文档处理能力，不含行业提示词、评分模型与私有知识库能力。

如果你**分发**本库（含修改版、含打包进你的产品），AGPL-3.0 要求你保留归属声明并向接收者提供完整对应源代码；如果你**通过网络提供服务**，第 13 条要求你向服务使用者提供获取对应源代码的方式。仅在组织内部使用不触发上述义务。
