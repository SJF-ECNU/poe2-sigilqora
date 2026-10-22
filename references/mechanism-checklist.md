# 制作机制功能索引：按需拓展操作候选

> 本表帮助查找能改变某项状态的机制，不是制作流程。根据问题按需检索相关功能；不要求每题逐项扫完或保留扫描日志。候选的使用资格和效果仍须由具体道具说明确认，不能只凭类目宣布合法。

| ID | 可检索的功能问题 | 可能改变的状态/成本 | 路径检索入口 | 不适用的常见理由 |
|---|---|---|---|---|
| M01 | 更合适的底材、ilvl、固有词缀、基础攻速/防御或特殊基础槽位吗？ | 减少竞争池；减少后处理需求 | 底材页、ModifiersCalc、Breach/Genesis | 用户不允许换 A；新底材不满足 B |
| M02 | 普通/高级/完美追加、稀有度转换是否经济？ | 增加一词、下限过滤、启动材料 | Currency | 当前稀有度/空槽不符 |
| M03 | 替换操作的可删集合、生成集合与稀有度要求是什么？ | 先删除再生成；每个后继状态独立计费 | Currency/Omen；`crafting-logic.md` | 必保的未分裂词会被删；不能用 C 生成特殊池词 |
| M04 | 精华是否提供保底词缀？它可作为永久词缀还是临时工具？ | 升稀有/删旧加 crafted | Essence | 该品阶在该部位没所需词缀；crafted 名额满 |
| M05 | 合金能否给出常规池没有的复合词缀或强化插槽？ | 强制复合词缀/替换 | Alloy / Essence | 该底材无此合金效果；crafted 冲突 |
| M06 | 左/右旋预兆能改新增端或删除端吗？ | 前后缀定向，保护 A 的值钱词 | Omen | 没有对应的通货；预兆效果与操作不匹配 |
| M07 | 能否改变抽取数量、按同类生成、按等级优先删除？ | 期望成功率、删除对象数 | Omen | 隐含条件不成立或破坏目标 |
| M08 | 能否用前后缀**满位**、词缀组互斥做封锁？ | 候选池的分母 | ModifiersCalc | 将目标一起封锁；删后重新开放 |
| M09 | 删除是否按等级、来源或其他标记选择？ | 锁词风险、失败修复成本 | Omen / Mark / 具体删除说明 | 最低等级并列；删除端不允许切它 |
| M10 | 什么来源改变crafted容量？来源消失后哪些结果存续？ | 当前容量、占用、来源与存续 | Rune / Astrid's Creativity | 当前 corrupted/sanctified；Socket-bound；替换后结果不保留 |
| M11 | 前/后缀容量可扩展吗？容量附加物可覆盖吗？ | 由 3/3 转到其他容量/锁定策略 | Rune / base / Delirium | 特殊增幅器绑定不可覆盖；部位不支持 |
| M12 | 可否利用普通/特殊的**可覆盖镶嵌物**进行中间操作？ | 中间达成前提→最后换更有用增幅器 | Rune, Soul_Core, Idol | Socket-bound；覆盖会令前置合法性失效 |
| M13 | 镶嵌物是否**解锁全新的词缀族**？ | 原本概率 0 变为可出现 | Rune special pool | 当前装备部位不适用；为永久 Socket-bound |
| M14 | 亵渎的资格、未揭示状态、来源池和揭示机制是什么？ | 新池、临时占位、分裂候选数量 | Abyss / Crafting | 亵渎名额满；特殊词缀阶段已结束 |
| M15 | 哪些词计入分裂门槛，哪些属于可抽选集合？ | 固定范围、计槽与合格候选分母 | Fracturing / Abyss | 目标不符合分裂资格；重买已分裂更便宜 |
| M16 | 品质的实际值、类型、可添加上限与消耗如何分别变化？ | 实际品质与可添加上限分开；释放临时前缀/crafted 名额 | Breach / Catalyst / Omen；`advanced-interactions.md` | 消费品质后无法无条件补回；标签不适用；权重需专用预兆 |
| M17 | 目标是否能从符文/灵核/雕像而非前后缀实现？ | 不占显式词缀，可能可替换 | Rune / Soul_Core / Idol | 缺孔；限制单个；羁绊不生效 |
| M18 | 目标值是否可通过放大**显式词缀效果或插槽效果**实现？ | 更高装备面板数值 | Alloy/Special Desecration | 非局部增益；同组或容量冲突 |
| M19 | 需要的是数值重骰、固有转化或抗性转化？ | 不重做已取得词缀 | Divine, Blessed Omen, Flux | 转化后与目标冲突；特殊状态不可操作 |
| M20 | 是否有专用珠宝工艺/范围/额外前后缀名额？ | 珠宝特有 crafted/槽位 | Delirium / Jewel | 不是相应珠宝类型（Basic vs Time-Lost） |
| M21 | 是否可以通过特殊底材生产流程解决？ | Breach Genesis/Wombgift/配方/重铸 | Breach, Verisium | 当前 A 无法变更底材；产物是随机新 A |
| M22 | 最终腐化/瓦尔/建筑师/牺牲/超品质道具有价值吗？ | 超上限/特殊附魔/多孔；高风险 | Fate of the Vaal/Corrupted | 用户禁止腐化；不可逆概率成本过高 |
| M23 | 腐化品是否有**可继续制作**的特殊后处理？ | 品质提升、牺牲改动、瓦尔吸取 | Fate of the Vaal | 目标对象类型或品质条件不符 |
| M24 | 传奇与特殊唯一码是否是更廉价的可用 B？ | Chance/Ancients/unique rune extraction | Currency/Unique/Rune | 不符合 B 的强制稀有度/底材 |
| M25 | 能否预见操作结果、减少不可逆损失？ | Hinekora's Lock、预示/保护 | Currency | 预见结果不可改变成必定成功；额外费用不值 |
| M26 | 直接购买精确 A'、已锁胚或 B 是否更划算？ | 省去昂贵的高风险步骤 | 同服同赛季交易市场 | 没有可比挂单或溢价不合理 |
| M27 | A 是药剂、护符或其他非典型装备部位吗？ | 特殊槽位、有限前后缀与独特品质材料 | Currency、对应装备分类（药剂/护符/箭袋等） | 是普通武器/护甲/首饰，且无需额外部位制作 |
| M28 | **全部目标词缀、保留词缀与制作材料保证词缀能否共存？材料使用前是否已经被现有词缀组阻挡？** | 发现隐藏词缀组和强制词缀冲突，提前淘汰伪路线 | Modifier Group、合金/精华原文、PoE2DAT、当期实测、`known-conflicts.json` | 已以明确证据证明兼容且使用资格无阻挡 |

## 如何使用索引

目标无法由已知候选达到、成本高或有未知交互时，用功能列拓展操作。对会改变可行性或显著成本的具体候选核对当前作用与资格；不需要为不相关的类别逐条编排排除理由。特殊底材、珠宝和腐化专用道具按对应装备查，不向每个普通装备问题强加同一份全表流程。

## 反向检索词典（需要时实际联网查）

- `site:poe2db.tw/us/Rune "Can have" "Crafted"`
- `site:poe2db.tw/us/Rune "Socket-bound" "Can roll"`
- `site:poe2db.tw/us/Essence "Maximum Quality" "Jewellery"`
- `site:poe2db.tw/us/Omen "lowest level modifier"`
- `site:poe2db.tw/us/Delirium "Modifier allowed"`
- `site:poe2db.tw/us "increased effect of Socketed Augment"`
- `site:poe2db.tw/us/Crafting "Desecration" "Fracturing"`
- `site:poe2db.tw/us/Fate_of_the_Vaal_items "Corrupted"`

**找不到 ≠ 不存在。**先换英文术语/同义词，查索引和当期补丁，再决定缺失是否阻止准确计算。不要编造概率填补信息缺口。
