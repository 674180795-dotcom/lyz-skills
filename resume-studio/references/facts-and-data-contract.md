# 事实与数据契约

## 三层数据

```text
candidate-ledger.json  私有事实、证据、疑点、确认状态
        +
role-analysis.json     JD/岗位要求、证据映射、缺口
        ↓
resume-data.json       只含允许公开和渲染的内容
```

事实、文案、布局和文件必须分开。修改岗位版本时复用同一份账本，不复制或改写原始事实。

机器可读定义：

- `assets/candidate-ledger.schema.json`
- `assets/role-analysis.schema.json`
- `assets/resume-data.schema.json`

可运行示例：

- `assets/example-ledger.json`
- `assets/example-role-analysis.json`
- `assets/example-resume.json`

## 事实账本

每个 `evidence_item` 至少记录：

- `id / kind / name / dates`
- `context`：面对什么问题或目标；
- `ownership`：本人做什么，团队做什么；
- `actions / methods`：真实动作与方法；
- `result`：数字或非数字结果；
- `proof`：用户确认、原简历、仓库、证书、正式文档等；
- `skills`：实际使用过的能力或工具；
- `status / confidence / uncertainties`。

允许证据类型：

- `source_resume`
- `user_confirmed`
- `repository_verified`
- `document_verified`
- `conservative_estimate`

`model_generated` 永远不是证据。保守估算必须使用“约、近、区间”等明确表达并由用户确认。

## 岗位分析

用户给 JD 时拆成：`must / preferred / responsibility`。每项只允许：

- `supported`：关联一个或多个 `evidence_ids`；
- `partial`：存在相关事实，但范围或深度不足；
- `gap`：无证据；
- `unknown`：尚未确认。

`gap` 不得通过把 JD 词汇抄进技能栏来消失。岗位知识只能帮助理解和提问，不能成为候选人事实来源。

## 多岗位

先判断证据集合是否相近：

- 相近：如产品经理 / AI 产品经理，共用母版并派生排序和措辞；
- 明显不同：如产品经理 / 平面设计师，生成两个独立 `role-analysis` 与 `resume-data`；
- 永远共用 `candidate-ledger`。

## 隐私

账本默认只留在用户指定的本地目录。不要收集身份证号、密码、令牌、宗教、婚育、民族、完整住址或无关健康信息。公开 HTML/PDF 不渲染 `source_note`、疑点和私人证据路径。

照片字段默认：

```json
"photo": {"enabled": false, "source": null}
```

只有用户主动要求并提供图片时开启。图片只用于排版；不得从外貌推断年龄、性别、民族、健康或其他敏感信息。上传的是旧简历截图时，它属于输入材料，不等于头像。
