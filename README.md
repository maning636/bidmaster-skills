# bidmaster-skills

**投标文档处理的技能集** —— 8 个技能，全部不依赖大模型，可完全离线运行。

做招投标 / 投标文件自动化时，有一堆脏活没人愿意重写：Word 排版、暗标脱敏、报价算术核查、格式一致性检查……这个库把它们做成**可组合的技能**，`pip install` 后直接调用。

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-81%20passed-brightgreen)](tests/)
[![LLM](https://img.shields.io/badge/LLM-not%20required-success)](README.md)

---

## 为什么值得一看

| 常见痛点 | 本库的解法 |
|---|---|
| Word 排版不可控：字体、字号、缩进、行距、页码，人工抄格式必出错 | `docx_format` 四种模式（排版 / 格式检查 / 模板对比 / XML 美化），能报告「哪一段字体不对」 |
| 投标文件带出公司名、作者、修订记录，暗标场景直接废标 | `anon_bid_clean` 扫描文档属性、页眉页脚 Logo、正文公司名、docProps |
| 报价表算术错误：单价×数量≠合价、大写小写不一致、超限价 | `pricing_check` 四类规则一次跑完，报出具体行号 |
| 检查结果散在十几个地方，没法交给人看 | `check_report_export` 渲染成 Markdown / HTML / 文本报告 |
| 自检靠人列清单，每次重来 | `selfcheck_list` 按检查结果自动生成清单，标出哪些还没过 |
| 规则散在代码里，改一条要发版 | `rules_screen` 规则包 JSON 驱动，改规则不改代码 |
| 风险靠感觉，说不清哪一维高风险 | `risk_score` 六维加权评分 |
| 大模型返回的 JSON 十次有一次是坏的 | `utils/json_repair` 多候选修复 + 逐级降级，不抛异常 |

## 8 个技能

全部 **零大模型依赖**，可完全离线运行。

| 技能 | 行数 | 作用 | 第三方依赖 |
|---|---:|---|---|
| `docx_format` | 947 | Word 排版 / 格式检查 / 模板对比 / XML 美化 | python-docx |
| `anon_bid_clean` | 501 | 文档属性与主体名称脱敏 | python-docx |
| `rules_screen` | 290 | 规则包筛选（JSON 驱动） | — |
| `check_report_export` | 244 | 检查报告导出（Markdown/HTML/文本） | — |
| `risk_score` | 210 | 六维加权风险评分 | — |
| `pricing_check` | 186 | 报价算术核查（限价/大写/单价×数量/安全区间） | — |
| `selfcheck_list` | 168 | 自检清单生成 | — |
| `self_score` | 83 | 自评分估算 | — |

另有三个基础包：`skill_engine/`（技能引擎）、`rules_engine/`（规则包读写）、`pathkit/`（路径解析）。

每个技能的完整契约见其目录下的 `SKILL.md`。

## 安装

```bash
pip install git+https://github.com/maning636/bidmaster-skills.git
```

第三方依赖只有 `python-docx` / `lxml` / `PyYAML`（后两个是 python-docx 的依赖）。

## 快速开始

### 报价算术核查（零依赖，最容易试）

```python
import asyncio
from skill_engine.base import SkillContext
from skills.pricing_check import PricingCheckSkill

bid_text = """
投标总价：98.5万
总金额：玖拾捌万伍仟元（985000）
1. 服务器 12.50 × 8 = 100.00
2. 交换机 3.20 × 10 = 35.00
"""

ctx = SkillContext(
    project_id="demo", db=None, llm=None,
    parameters={"bid_text": bid_text, "max_price": 100.0},
)
result = asyncio.run(PricingCheckSkill().execute(ctx))

print(result.data["risk_level"])     # high
for c in result.data["checks"]:
    print(c["status"], c["check_type"], c["detail"])
```

输出（第 2 项算错 3 万，报价又贴着限价 —— 两处都会被人工漏掉）：

```
pass    price_limit      投标总价98.5万未超过限价100.0万
pass    upper_lower_case 大写:玖拾捌万伍仟元 小写:985000元 (需人工确认一致)
fail    arithmetic       第2项: 3.2×10.0=32.00≠35.0
fail    safe_range       报价为限价98.5%，超出98%安全带上限
```

### Word 排版检查

```python
import asyncio
from skill_engine.base import SkillContext
from skills.docx_format import DocxFormatSkill

ctx = SkillContext(
    project_id="demo", db=None, llm=None,
    parameters={"file_path": "你的标书.docx", "mode": "check"},
)
result = asyncio.run(DocxFormatSkill().execute(ctx))

print(result.data["total_issues"])        # 1218（真实标书实测：739 段 / 2149 run）
print(result.data["compliance_rate"])     # 43.3
```

`mode` 支持 `format`（排版）/ `check`（检查）/ `diff`（与模板对比）/ `beautify`（XML 美化）。

### 暗标脱敏

```python
ctx = SkillContext(
    project_id="demo", db=None, llm=None,
    parameters={
        "file_path": "投标文件.docx",
        "company_names": ["某某科技有限公司", "某某科技"],
        "region": "beijing",          # national / beijing / guangdong / jiangsu
    },
)
result = asyncio.run(AnonBidCleanSkill().execute(ctx))
print(result.data["passed"])          # 有 critical 项时为 False
```

### 修复坏 JSON（大模型输出兜底）

```python
import asyncio
from utils.json_repair import JsonRepairEngine

engine = JsonRepairEngine()

# 剥掉 <think> 标签与 markdown 代码块
print(engine.extract_json('```json
{"a": 1}
```'))   # {"a": 1}

# 修复常见破损（尾逗号 / 裸键 / 未闭合括号），失败不抛异常
fixed = asyncio.run(engine.repair_and_validate('{"a": 1, "b": [1,2,], }'))
print(fixed)                                             # {'a': 1, 'b': [1, 2]}
```

## 设计：为什么用「技能」而不是函数

每个技能都是 `Skill` 子类，实现统一的 `execute(ctx) -> SkillResult`：

```python
class Skill(ABC):
    name: str
    description: str
    category: str
    version: str
    triggers: list[str]
    required_plan: str = "free"

    @abstractmethod
    async def execute(self, ctx: SkillContext) -> SkillResult: ...
```

好处：

- **统一错误处理**：失败返回 `SkillResult(success=False, error=...)`，不抛异常
- **统一进度回调**：长任务可通过 `ctx.progress_callback` 推进度
- **可组合**：一个技能的输出（`SkillResult.data`）可以直接喂给下一个技能
- **易测试**：不依赖 Web 框架、不依赖数据库（`db` / `llm` 都可为 `None`）

## 目录结构

```
skill_engine/          # 技能引擎（基类 / 上下文 / 结果 / 注册表 / 加载器）
rules_engine/          # 规则包读取与过滤（纯标准库）
pathkit/               # 路径解析（app_root / data_root）
skills/                # 8 个技能，每个含 SKILL.md
  docx_format/
  anon_bid_clean/
  rules_screen/
  check_report_export/
  risk_score/
  pricing_check/
  selfcheck_list/
  self_score/
utils/json_repair.py   # 坏 JSON 修复
examples/              # 最小可跑示例
tests/                 # 81 条测试
```

## 测试

```bash
pip install -e ".[dev]"
pytest
```

81 条，全部不依赖网络、不依赖真实标书文件、不调大模型。

## 边界（诚实说明）

- **不含任何提示词**：解读、生成、围串标识别等需要大模型的能力不在本库
- **不含私有知识库**：检索增强能力在主产品里，不在开源部分
- **`docx_format` 只处理 .docx**：不处理 .doc / PDF / OFD
- **正则匹配针对常见排版**：特殊格式可能漏匹配，此时对应检查项会返回 `warning` 而非静默通过
- **`pricing_check` 只查算术与格式**：不判断报价是否「合理」，不预测中标概率

## 许可

**AGPL-3.0**。全文见 `LICENSE`。

本库的 `skill_engine/`、`skills/docx_format/` 与 `utils/json_repair.py` **派生自 AGPL-3.0 上游项目** [BidMaster-Pro](https://github.com/guangshu100/BidMaster-Pro)（经由「老马标书贤内助」主仓），因此本仓库整体必须保持 AGPL-3.0，**不得改为 MIT 或其他更宽松许可**。上游归属与实测相似度见 `NOTICE`。

如果你**分发**本库（含修改版、含打包进你的产品），AGPL-3.0 要求你保留归属声明并向接收者提供完整对应源代码；如果你**通过网络提供服务**，第 13 条要求你向服务使用者提供获取对应源代码的方式。仅在组织内部使用不触发上述义务。

## 相关

- 单技能精简版（零依赖，只含 `pricing_check`）：[bidmaster-pricing-check](https://github.com/maning636/bidmaster-pricing-check)
