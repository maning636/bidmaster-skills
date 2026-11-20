# 给下游 Agent · 上线说明（8 技能版）

> 自包含任务书。读完即可开工，不需要主会话上下文。

---

## 1. 现状（已完成）

| 项 | 状态 |
|---|---|
| 本地仓库 | ✅ `D:/dim开发/laoma-bid-skills` |
| GitHub | ✅ **Public**：https://github.com/maning636/laoma-bid-skills |
| 技能数 | **8 个**，全部零大模型依赖 |
| 测试 | ✅ **81 条全绿** |
| 许可 | AGPL-3.0 + NOTICE（上游归属写清） |
| 从 GitHub 安装 | ✅ 实测通过 |
| CI | ✅ `.github/workflows/ci.yml` 已配 |

**代码侧不用再动。** 剩下是运营工作。

---

## 2. 这是什么

投标文档处理的**技能集**。8 个技能，可组合、可独立调用：

| 技能 | 作用 | 第三方依赖 |
|---|---|---|
| `docx_format` | Word 排版 / 格式检查 / 模板对比 / XML 美化 | python-docx |
| `anon_bid_clean` | 文档属性与主体名称脱敏（暗标场景） | python-docx |
| `rules_screen` | 规则包筛选（JSON 驱动） | — |
| `check_report_export` | 检查报告导出（MD/HTML/文本） | — |
| `risk_score` | 六维加权风险评分 | — |
| `pricing_check` | 报价算术核查 | — |
| `selfcheck_list` | 自检清单生成 | — |
| `self_score` | 自评分估算 | — |

**5 个技能零第三方依赖**，另 3 个只依赖 python-docx。

---

## 3. 你要做的事

### P0 · 验证现状（0.5 小时）

```bash
cd /tmp && rm -rf _v && mkdir _v && cd _v
"D:/dim开发/_bidmaster/.venv/Scripts/python.exe" -m pip install --no-deps --target ./site \
  "git+https://github.com/maning636/laoma-bid-skills.git"
PYTHONPATH=./site "D:/dim开发/_bidmaster/.venv/Scripts/python.exe" -c "
import asyncio
from skill_engine.base import SkillContext
from skills import PricingCheckSkill
ctx = SkillContext(project_id='d', db=None, llm=None,
    parameters={'bid_text':'投标总价：105万', 'max_price':100.0})
r = asyncio.run(PricingCheckSkill().execute(ctx))
print('risk:', r.data['risk_level'])   # 期望 high（超限价）
"
```

浏览器打开仓库，确认 README 渲染正常、8 技能表格显示完整。

### P1 · 补 GitHub 元信息（1 小时）

| 项 | 做法 |
|---|---|
| **Topics** | Settings → Topics，加：`bidding` `tender` `procurement` `docx` `chinese` `document-processing` `skill-engine` `python` `agpl` `招投标` `标书` |
| **About** | 一句中文 + 一句英文。例：「投标文档处理技能集 · 8 个零大模型依赖的可组合技能 / 8 LLM-free composable skills for Chinese tender documents」 |
| **Release v0.1.0** | 打 tag，notes 列 8 个技能 + 安装命令 + 81 条测试 |
| **CI 徽章** | README 里换真实的 CI 状态徽章（当前是静态文本） |

### P2 · 发 PyPI（2 小时）

```bash
pip install build twine
python -m build
twine upload --repository testpypi dist/*   # 先验 TestPyPI
twine upload dist/*                          # 再发正式
```

发完 README 的安装命令改成：
```bash
pip install laoma-bid-skills
```

**注意**：先查 https://pypi.org/project/laoma-bid-skills/ 是否被占。

### P3 · 内容分发（1–2 天）

| 渠道 | 角度建议 |
|---|---|
| 掘金 / 知乎 / CSDN | 「投标文件排版 1218 处错误，人工核三天」——用真实数字开场 |
| V2EX / Reddit r/Python | 「8 个零 LLM 依赖的文档处理技能」——强调不调大模型这个差异化 |
| 微信公众号 | 实战案例：某次废标是因为文档属性里留着作者名 |

**关键**：不要写「我做了个库」，写「这 3 个错误会让你直接废标，附检测代码」。前者没人看，后者有搜索价值。

---

## 4. 两个仓库的关系

| 仓库 | 内容 | 定位 |
|---|---|---|
| **laoma-bid-skills**（本仓库） | 8 个技能完整版 | 主推，面向团队/项目使用 |
| laoma-bid-pricing-check | 只含 `pricing_check` | 单技能精简版，零依赖，面向快速试用 |

**建议**：README 里已互相引用。推广时先推单技能版（门槛低），引导到完整版。

---

## 5. 未来要「封闭」时

| 方案 | 做法 | 注意 |
|---|---|---|
| **转私有** | Settings → Danger Zone → Change visibility → Private | 已 clone 的人不受影响，已 fork 的不会消失 |
| **Archive + 转私有** | 先 Archive（只读）再转 Private | 更彻底，明确表示不再维护 |

**AGPL 义务**：如果有人已 clone / pip install 过，AGPL 要求向他们提供源码。**转私有不能追溯撤销已发生的分发义务。**

---

## 6. 红线

1. **不许改许可证** —— AGPL-3.0 是事实性约束（派生自 BidMaster-Pro）
2. **不许删 NOTICE 的上游归属**
3. **不许把主仓的提示词、评分模型、私有知识库搬进来**
4. **不许用真实标书做示例**（当前示例是构造文本）
5. **不许 `git push --force`**（已公开）
6. **新增技能必须同时给 `SKILL.md` + ≥3 条测试**

---

## 7. 需要用户提供

| 项 | 用途 |
|---|---|
| PyPI 账号 / API token | P2 发版 |
| 官网地址 | P1 About、README |
| 微信群/公众号二维码 | `docs/assets/`（当前未放） |

---

## 8. 验收标准

- [ ] `pip install git+https://github.com/maning636/laoma-bid-skills.git` 成功
- [ ] 8 个技能全部可 import
- [ ] `pytest` 81 条全绿
- [ ] GitHub Topics ≥ 6 个、About 已填
- [ ] Release `v0.1.0` 已发布
- [ ] CI 徽章显示 passing
- [ ] README 在 GitHub 上渲染正常
- [ ] 外部人（非本机）能装能跑

---

## 9. 参考

- 主仓：`D:/dim开发/_bidmaster`
- 单技能版：`D:/dim开发/laoma-bid-skills-pricing`
- 各技能契约：`skills/*/SKILL.md`
- 上游归属：`NOTICE`
