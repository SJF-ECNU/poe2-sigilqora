# 知识覆盖与证据边界

2026-10-22系统审查，范围为现有329项索引与基础制作机制。原始目录和关键词说明来自PoE2DB提取的游戏文本，版本变动对照GGG0.5.0；用户确认/玩家记录另行标记。没有执行游戏点击或DSH行为验收。

## 实际覆盖

`item-descriptions.json`保留独立原始描述，生成器将其合并到现有道具记录；不是制作配方。`effect_coverage=source_description`仅表示有原文，不等于隐藏组、随机选择顺序或一切联动已验证。

| 类别 | 名称数 | 已有具体原文 |
|---|---:|---:|
| Abyss Bone | 12 | 12 |
| Aldur Rune | 4 | 4 |
| Alloy | 13 | 13 |
| Ancient Augment | 4 | 4 |
| Basic Rune | 63 | 63 |
| Catalyst | 26 | 26 |
| Currency | 37 | 33 |
| Essence | 76 | 76 |
| Expedition Currency | 1 | 1 |
| Fate of the Vaal | 12 | 12 |
| Meta Augment | 4 | 4 |
| Omen / Saga | 50 | 49 |
| Pool-Unlocking Rune | 5 | 5 |
| Resistance Flux | 4 | 4 |
| Rune | 1 | 1 |
| Rune Production | 1 | 1 |
| Sacrifice Orb | 4 | 4 |
| Special Essence | 6 | 6 |
| Special Jewellery Base | 6 | 6 |

合计324项有具体原文。仍只有族级/身份说明的5项：Artificer's Shard、Chance Shard、Regal Shard、Transmutation Shard、Omen of Recombination。前4项是合成碎片而非直接装备操作；Recombination为历史入口，不能默认当前取得。

## 已校正的基础问题

- 稀有度与容量、门槛计数与抽选资格、Tier/mod level/需求等级/数值分别表示。
- 精华和合金补齐已提取的逐部位效果，普通输入与特殊词来源不互代。
- 预兆记录独立触发阶段和改写部分；所有特殊精华归入对应腐化精华关系，合金联动记录具体确认范围。
- Jeweller涵盖装备授予技能的辅助孔；Artificer明确增幅孔适用类别。
- Siphoner为随机降阶而非删词；圣化/部分腐化数值结果依赖当前值。
- Mark的指定替换机制、Altered Collarbone的otherworldly可能性、Bonded条件和Standard限定预兆单独保留。
- 功能检索不静默丢查询条件，紧凑输出保留target及完整作用；池发现/可生成、截断/全阶级、权重占比/实际概率分开。
- 费用按不同后继状态递推，部分有效报价保留，缺价/异常不变成免费或完整总成本。

## 尚不能由这些数据确定

ModFamilyList是否精确等于最低等级例外的modifier type、例外的客户端完整算法、删除集合为空时具体通货的后续行为、满词亵渎的删侧/加侧顺序、多预兆联合消费顺序、隐藏组、真实催化倍率与部分随机权重仍有边界。具体字段未知时保留变量或条件结果，而不是由目录推测。

特殊容量来源覆盖后的已有结果存续按具体机制/版本判断，不外推为所有临时工具的通则。确定的Socket-bound不可移除、Extraction毁装等风险保留。合金结晶预兆联动在用户确认的0.5语境中复用，摘要未提及不作为否定证据。

此目录不穷尽所有新增材料、所有专用增幅器或底材生产规则。已有原文可按需取用；缺少相关具体效果才扩展对应数据。
