# 贡献指南

1. Fork → 新建分支 `feat/xxx`
2. 跑 `pytest tests/ -q` 与 `ruff check .`（都不许红）
3. 若新增技能：按 `examples/hello_skill/` 的目录布局放 `SKILL.md` + `skill.py`
4. PR 描述里写清「解决什么问题、怎么验证」

## 不接受的内容

- 含真实投标文件、企业资质、联系方式的样例
- 任何形式的付费提示词或私有知识库数据
- 与 AGPL-3.0 不兼容的依赖

## 代码风格

- 类型注解完整；异常不外泄（技能内统一转成 `SkillResult(success=False, error=...)`）
- 注释只写「为什么」，不写「做了什么」
