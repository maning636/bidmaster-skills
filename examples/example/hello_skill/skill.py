"""最小示例技能：文本转大写。"""
from __future__ import annotations

from skill_engine.base import Skill, SkillContext, SkillResult


class HelloSkill(Skill):
    name = "hello_skill"
    description = "把输入文本转成大写"
    category = "example"

    async def execute(self, ctx: SkillContext) -> SkillResult:
        text = str(ctx.parameters.get("text", ""))
        return SkillResult(success=True, data={"upper": text.upper()})
