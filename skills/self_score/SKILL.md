# self_score · 自评分估算

提交前按评分矩阵估算得分并标注薄弱项。纯规则判定，不调用大模型，不依赖数据库。

## Agent 什么时候该调用我

**该调用：**

- 用户问「大概能得多少分」「哪些项会丢分」
- 已有评分项列表 + 各章节内容，需要粗估

**不该调用：**

- 没有评分项列表 → 先从招标文件解读出评分标准
- 用户问「怎么提高得分」→ 这是策略，你自己回答
- 需要「精确预测评标分数」→ 本技能只是按内容长度分档粗估，不精确

**诚实提示：** 这是**粗估**，按「内容长度 ≥500 字算充实」这种规则打分，
不代表真实评标结果。回答用户时要说清这一点。

## 输入

`execute` 只读 `ctx.parameters`：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `scoring_rows` | list[dict] | 是 | 评分项，每项含 `item`、`score`（满分）、`category` |
| `blocks` | list[dict] | 否 | 章节内容块，每项含 `title`、`score_items`、`content_length` |

`scoring_rows` 为空时返回失败。

## 输出

`SkillResult.success = True`，`data` 结构：

```json
{
  "items": [{"item": "...", "category": "...", "max_score": 10.0,
             "estimated_score": 9.0, "loss": 1.0, "reason": "...", "is_weak": false}],
  "total_max": 100.0,
  "total_estimated": 72.0,
  "estimated_percentage": 72.0,
  "weak_items": [{"item": "...", "loss": 3.0}],
  "weak_count": 1,
  "recommendation": "..."
}
```

## 估算规则

每个评分项关联到 `blocks` 中匹配的章节（按 `score_items` 或标题关键词），
取内容最长的一个，按 `content_length` 估分：

- ≥500 字 → 满分的 90%
- ≥200 字 → 满分的 70%
- >0 字 → 满分的 40%
- 空/未找到章节 → 0 分，原因标注

`is_weak` 为估分 < 满分的 60%。`weak_items` 为丢分最多的前 5 个薄弱项。

## 属性

- `name = "self_score"`，`category = "check"`，`version = "1.0.0"`
- `triggers = ["自评分", "预估分数", "评分估算"]`
