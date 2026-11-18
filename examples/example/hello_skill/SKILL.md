---
name: hello_skill
description: 最小示例技能：把输入文本转成大写，用来演示技能引擎的加载与执行。
metadata:
  category: example
  version: 0.1.0
---

# hello_skill

最小可运行示例。演示三件事：

1. `SKILL.md` 的 front-matter 如何声明 `name` / `description` / `metadata`；
2. `skill.py` 里如何实现 `Skill` 子类（`execute` 返回 `SkillResult`）；
3. 引擎如何按目录布局发现并注册它。

```python
from skill_engine.loader import SkillLoader
from skill_engine.registry import SkillRegistry

loader = SkillLoader("examples")
loader.load_all()
for key in loader.load_all():
    SkillRegistry.instance().register(loader.get_skill_class(key))
```
