# 道具操作硬约束、误区与证据等级

**审计日期：2026-10-22。**本文件不是词缀数据库，而是记录具体条件、风险与证据范围的参考。按作用或逐名查询已有记录；同版本已核实的作用可复用，条目仅有族级信息、版本不明或组合存在缺项时，再到具体来源定点确认。`category-contract` 只表示族级规则已查，**不代表每件物品的数值、部位或组合已逐项核实**。

## A. 如何使用本页

这里保存具体使用条件与不可逆后果。按候选涉及的机制查看，已核实的同版本事实可直接复用；未知条件保留为条件分支，执行不可逆操作前仍需明确其资格与后果。一般状态定义见 `state-and-planning.md`，独立道具原文由lookup返回。

## B. 已核对的关键跨材料规则

| 编号 | 严格规则 | 出错的典型后果 | 核对入口 |
|---|---|---|---|
| R01 | **Minimum Modifier Level 不是无条件删光低等级词缀**：若某一具体词缀类型会被完全排除，存在保留该类型可用阶级的例外。先区分 `mod level`、`item level`、`required level`。 | 误以为高级 C 或完美崇高能把某词缀家族变为 0 权重，高估 T1 命中率。 | https://poe2db.tw/us/Minimum_Modifier_Level |
| R02 | **具有 Minimum Modifier Level 的通货不能施加在 ilvl 低于该门槛的物品上**。例如 ilvl 49 不能用 Minimum Modifier Level 50 的完美 C/崇高（按当期道具原文确认）。 | 计划在低等级极品底材上无限完美 C，实际无法使用。 | https://poe2db.tw/us/Currency |
| R03 | **普通/高级/完美蜕变、增幅、富豪、崇高、C 的适用稀有度不同**；点金从白/蓝生成四条，C 对稀有物品先删一条再加一条。 | 从错误的 rarity 执行；把删除和新增合并算一个池。 | https://poe2db.tw/us/Currency |
| R04 | **低/普通/高阶精华**：魔法 → 稀有，添加其部位对应 guaranteed modifier；**完美及腐化精华**：在稀有装备上随机删一条再添加对应 guaranteed modifier。 | 将完美精华误当作固定加词且不丢原词缀。 | https://poe2db.tw/us/Essence |
| R05 | **精华保证效果由品阶和装备部位共同决定**，名称相同不代表效果同族：`Greater Essence of Flames` 武器加点火；`Perfect Essence of Flames` 武器获得额外火伤；`Perfect Essence of Haste` 给武术武器击杀获得猛攻概率，并非 T1 攻速。 | 根据名字联想强制词缀，直接制作失败。 | https://poe2db.tw/us/Essence |
| R06 | 合金在稀有物品上**先随机删除，再添加部位指定的 crafted 词缀**；精华与合金共享 crafted 名额（0.5 默认 1）。已有互斥词缀时**使用资格可能先判断**，不能假设合金会先删掉阻挡者。影响精华的结晶预兆也能作用合金，有 Wiki 明文和玩家制作记录支持，不能按“名字不是精华”排除。 | 误判只能在成品上裸赌合金；或将同组/名额已满的操作当合法。 | https://poe2db.tw/us/Essence ; https://www.poe2wiki.net/wiki/Alloy ; https://www.reddit.com/r/PathOfExile2/comments/1tx3u8c/my_first_big_craft_7_lightning_gem_wand_for_my/ |
| R07 | 相同装备部位上的词缀需要同时满足普通互斥组、crafted 来源容量、亵渎上限、特殊来源条件；**网页两条词缀同时存在≠可以同件共存**。 | 计算出不可能存在的装备。 | https://poe2db.tw/us/Modifiers ; `compatibility-and-evidence.md` |
| R08 | **预兆是对下一次指定操作的改写**；左/右旋可能只约束删除侧，也可能只约束新增侧，不得混写。`Omen of Catalysing Exaltation` 作用在**下一颗 Exalted Orb**，会**消耗全部对应 Catalyst Quality**提高匹配词缀概率，不是 100% 命中。 | 省略触发通货成本，或错误保护好词缀。 | https://poe2db.tw/us/Omen |
| R09 | `Omen of Whittling` 改写下一颗 C 的**删除端**，优先移除最低等级词缀；比较字段是mod level，不能用显示的装备需求等级或Tier代替。遇到并列要核对处理。 | 当牺牲位等级并不最低时误删目标词。 | https://poe2db.tw/us/Omen_of_Whittling ; https://poe2db.tw/us/Essence_of_the_Breach |
| R10 | **普通非绑定增幅器可被后续增幅器覆盖**，被覆盖旧材料通常不会退还；`Socket-bound` 一旦镶嵌就**不能以任何方式移除、替换或抽取**。`Astrid's Creativity` 可增加 crafted 容量；覆盖后两条 crafted 词缀存续属于社区观察，**要重新验证版本**。 | 临时工具锁死最终孔位；错误计算“可拿回来”的残值。 | https://poe2db.tw/us/Keywords ; https://poe2db.tw/us/Astrids_Creativity |
| R11 | `Orb of Extraction` 是**销毁整件装备**并返还其中**非 Socket-bound** 增幅器，绝非免费拆卸符文。 | 误操作摧毁成品。 | https://poe2db.tw/us/Fate_of_the_Vaal |
| R12 | **深渊骨**按武器/护甲/首饰/珠宝/碑牌和 Gnawed/Preserved/Ancient 等分支，添加可揭示亵渎词缀；必须核对初始稀有度、ilvl 限制、亵渎上限、未揭示状态与特殊池。骨头带有最低词缀等级时亦需检查适用资格。 | 高等级装备使用 Gnawed；把亵渎看作普通随机词缀。 | https://poe2db.tw/us/Abyss |
| R13 | **破裂石**的目标概率按**实际合格候选词缀**计数；在当前机制下，未揭示的亵渎词缀可满足数量门槛却不参与破裂候选，但必须验证装备状态、各词缀可破裂性和成本。 | 一律用 `1/总词缀数` 计算。 | https://www.poe2wiki.net/wiki/Fracturing_Orb |
| R14 | **Catalyst** 的品类品质会替换其他 Catalyst Quality；用于增加权重的预兆可能全部消耗品质；普通武术武器品质提高物理伤害；护甲品质还作用Runic Ward，授予技能的物品另有技能品质效果。 | 错把 30% 武器品质叠到攻速计算；忘记恢复催化品质的成本。 | https://poe2db.tw/us/Quality ; https://poe2db.tw/us/Omen |
| R15 | **Vaal Infuser 是分次提升品质、有腐化风险的操作**；要至少 20% 品质，**且达到当前有效最大品质**（底材/词缀有更高 Maximum Quality 时不能只凭 20% 判定可用）；作用对象严格区分武术武器/施法武器/护甲/戒指及项链，最多额外 +10%。成功增量、腐化率属于非确定概率，不能以“首次实测未腐化”视作官方 0 风险。 | 20% 以下使用、拿腰带当目标、将多次概率当一次固定 +10%。 | https://poe2db.tw/us/Fate_of_the_Vaal ; https://www.pathofexile.com/forum/view-thread/3932540 |
| R16 | **实际品质与当前可添加上限分开**：`Essence of the Breach` 为首饰提供 `+20% Maximum Quality` crafted 前缀；移除此词时，**已添加品质保留，前缀位和 crafted 名额释放**（用户确认及玩家记录，详见 `advanced-interactions.md`）。`Breach Ring` 等也可提高上限。移除来源会降低此后可添加的上限，不代表回退已存品质；耗尽/换品质后的恢复受当时可添加上限约束。 | 把可添加上限误当已存品质；消费品质后漏算恢复上限的风险和成本。 | https://poe2db.tw/us/Essence_of_the_Breach ; `advanced-interactions.md` |
| R17 | **腐化之后并非绝对不能再操作，但仅可使用当期明确允许作用于腐化物品的手段**；`Architect's Orb` 可能毁掉腐化装备或珠宝；4 种 `Orb of Sacrifice` 会强化腐化附魔且**随机删一条词缀**。 | 把腐化后常规 C 当合法，或将牺牲强化当免费。 | https://poe2db.tw/us/Corrupted_Items ; https://poe2db.tw/us/Fate_of_the_Vaal |
| R18 | 神圣预兆 `Omen of Sanctification + Divine Orb` 圣化尚未圣化的稀有装备；**同件只能圣化一次，圣化后无法再改变**，不能再神圣或重复圣化。0.5按当前词缀值乘倍率，不先重掷普通范围；所需数值、词缀、品质与插槽处理先完成。 | 把未达目标的圣化结果当作可重骰/重试，编造原件上的恢复路线。 | 用户确认当前0.5终态限制；https://www.poe2wiki.net/wiki/Sanctified ; https://poe2db.tw/us/Omen |
| R19 | **Flux 有两个不同体系**：`Blazing/Chilling/Crackling/Void Flux` 转换的是抗性词缀；`Passion/Breath/Ire/Betrayal of Aldur` 是插槽绑定的武器**元素词缀转换**，不可混为一谈。 | 把元素点伤当成已转换，或漏掉永久占孔。 | https://poe2db.tw/us/Resistance ; https://poe2db.tw/us/Modifiers |
| R20 | `Runeforging` 是 400+ 个与**底材、Verisium 数量**有关的配方，不是泛泛“强化底材”；要反查具体输入→产物及特殊属性变化。`Perfect Flux` 与抗性 Flux 是另一种道具。 | 忽略有价值底材转换，或者将不存在的配方写进步骤。 | https://poe2db.tw/us/Runeforging ; https://poe2db.tw/us/Perfect_Flux |
| R21 | 预兆/增幅器可能是不可再获得的历史版道具，`Omen of Recombination` 等不能因旧索引而视作当前可取得；Homogenising Exaltation/Coronation在0.5仅于Standard货币交易出现。某些“16 件瓦尔物品目录”包含**底材和增幅器**，还缺其他分类收录的牺牲石。 | 用不可获得道具算最低成本，或误认为瓦尔总共 16 种。 | https://poe2db.tw/us/Omen ; https://poe2db.tw/us/Fate_of_the_Vaal |
| R22 | 药剂、护符、普通珠宝/时失珠宝、碑牌、特殊首饰与其他装备的适用范围不同；不要把地图物品和装备 crafting 混算。`Penumbra/Tenebrous` 等特殊底材可能直接改变 3/3 前后缀默认上限。 | 对错误物品类别使用精华；漏掉改变容量的底材。 | https://poe2db.tw/us/Modifiers ; https://poe2db.tw/us/Delirium |

## C. 特殊品质门槛与不可逆操作

四类Vaal Infuser的具体对象不同：Blacksmith为Martial Weapon，Arcanist为Wand/Staff/Sceptre，Armourer为Armour，Catalysing为Ring/Amulet而非Belt。要求至少20%且达到当前有效Maximum Quality；有更高上限来源时不能仅凭20%判断可用。逐次增加、累计最多超上限+10%，每次可能腐化；单次增量和腐化概率未知则不赋确定值。原文包含 `Can only be used on items at or above maximum quality`，见 [Fate of the Vaal](https://poe2db.tw/us/Fate_of_the_Vaal)。

销毁、腐化、圣化、Socket-bound和分裂锁错应保留独立失败状态与真实损失。未解决的资格、删除对象或后续可用性不能填成0%/100%；可以给条件计算，不能将未知分支当作确定可执行的点击建议。
