# 制作数据与国服 / 国际服材料价格

## 1. 职责分界

- **道具做什么**：用 `lookup_item.py` 按名称/作用查询已有记录；缺失的部位效果或版本差异再查该道具原文。
- **该装备能出什么、概率多少**：使用底材所属类别的词缀池，结合具体底材的特殊限制；按 ilvl、家族互斥、生成标签、当前空槽、通货 Minimum Modifier Level（含**整个 modifier type 被排空时的保留例外**）、**目标 ilvl 不能低于道具该门槛**筛选本轮候选池，抽取权重现场算。
- **材料现在多少钱**：只用 `scripts/prices.py` 调用当前市场的经济接口；换算时必须严格保留 realm、league、报价币种、刷新时间、异常信息。
- **当前装备 A、特定锁词缀胚、目标成品 B、失败半成品价格**：交易市场挂单，需要用户或 Agent 另行按具体底材/词缀查询；无法用通货行情均价冒充装备交易价。

## 2. poe2db 入口（运行时按需打开）

| 需要的信息 | 入口 | 特别注意 |
|---|---|---|
| 基础道具、武器攻速 | https://poe2db.tw/cn/Spears / 各装备分类 | 以**当前底材实际值**为准，且分辨局部 vs 全局词缀 |
| 具体底材的可生成词缀和权重 | 装备类别页面的词缀计算 / ModifiersCalc | 类型、ilvl、普通/特殊来源、实际权重、同组不可共存 |
| 普通/高级/完美通货 | https://poe2db.tw/cn/Currency | 适用稀有度、最低新增词缀等级、先删除再新增 |
| 预兆 | https://poe2db.tw/cn/Omen | 生效的“下一种操作”；修改删除端还是新增端 |
| 精华和合金 | https://poe2db.tw/cn/Essence | 具体品阶与具体部位上的**实际保证词缀** |
| 深渊骨和亵渎 | https://poe2db.tw/cn/Abyss | 适用类别、揭示流程、特殊词缀池、概率 |
| 催化剂、符文、灵核与增幅器 | https://poe2db.tw/cn/Breach / https://poe2db.tw/cn/Rune / https://poe2db.tw/cn/Soul_Core | 品质、部位效果、局部/全局机制、可覆盖性和羁绊 |
| 亵渎/占位与分裂候选 | https://poe2db.tw/us/Crafting / https://www.poe2wiki.net/wiki/Fracturing_Orb | 亵渎计槽但不可分裂；当前状态的实际候选数量 |
| 珠宝保底和特殊容量 | https://poe2db.tw/us/Delirium / https://poe2db.tw/us/Ancient_Potent_Liquid_Contempt | Basic/Time-Lost、前后缀额外容量、crafted 名额 |
| 元增幅器和绑定性 | https://poe2db.tw/us/Rune / https://poe2db.tw/us/Keywords | Astrid 可覆盖与 Serle/Thrud 等 Socket-bound 的差异 |
| 瓦尔/腐化后处理 | https://poe2db.tw/us/Fate_of_the_Vaal_items / https://poe2db.tw/us/Corrupted | 超品质至少20%、4件献祭石会删词；Fate /16 并非瓦尔制装全集 |
| 高级通货规则原文 | https://poe2db.tw/us/Minimum_Modifier_Level | 最低物品等级限制；**不会把某词缀类型全部排空的例外** |
| 品质/催化剂与品质上限 | https://poe2db.tw/us/Quality / https://poe2db.tw/us/Catalysts | Catalyst 标签品质、逐次高品质、来源是否还存在 |
| 符文锻造配方/转换道具 | https://poe2db.tw/us/Runeforging / https://poe2db.tw/us/Resistance | 逐件搜底材+Verisium成本与元素抗性转换 |

poe2db 某些列表即使展示 Weight 字样，若所有行看似占位数值、或注明权重不能从游戏文件中直接提取，**不得把占位权重当作真实概率**。可以使用该页有明确说明的估算权重，但需交代准确度。

### 页面提取不完整与数据缺失是两回事

搜索摘要、道具页和静态网页提取可能不包含交互式 ModifiersCalc 的明细。若未见词缀组或权重，不能据此断言游戏不存在该词或组合；HTTP 403 也只是当前取数方式失败。

可用环境有浏览器工具时，打开具体底材的词缀计算器，设置物品类别、ilvl、现有词缀与操作条件后检查明细；不要把未设置状态的总池当作本轮池。可交叉看 PoE2DAT 等模拟器的同一状态，但先辨别其 Tier 编号方向、候选池是否含特殊词，以及 Weight/概率是实际、估算还是占位。模拟器允许共存不能单独推翻游戏互斥证据。

缺精确权重或催化倍率时，把能查明的作用与仍缺的数值分开；用变量或可信范围比较成本，不从论坛单个成功/失败案例倒推精确概率。也不因为缺一个倍率就否定整个组合，或用另一个默认策略替代计算。

## 2.1 材料逐名契约与来源可信度

按名字或作用使用 lookup 查询该材料及关联操作；不打印整份记录库。当前状态的适用性仍按 `references/critical-rules.md` 核对，同版本已核实的作用不机械重复联网。`verification_level` 只表示离线核实层次：`item_effect_reviewed` 属于道具作用级别审阅，`category_contract` 是族级通用规则，`family_name_not_individually_live_verified` 需要优先查询英文道具详情。它们不代表对任意装备/新版本都已验证；具体缺项按需查来源。特别是部分物件列在 `Fate of the Vaal Item /16` 以外，不能据此排除献祭石和各种 Flux。

## 3. 材料价格脚本（Python 标准库，无三方依赖）

从当前工作区运行脚本路径；缓存默认写工作区 `.pcache/poe2-prices`，也可显式 `--cache-dir <工作区路径>`：

```bash
# 先确认市场与赛季，不接受自动跨服补价
python scripts/prices.py leagues --realm intl
python scripts/prices.py leagues --realm cn

# 国际服：赛季ID可以指定，也可以 current 表示目录中的当前挑战赛季
python scripts/prices.py quote --realm intl --league current \
  --category Currency --item "Perfect Exalted Orb"
python scripts/prices.py quote --realm intl --league "<league_id>" \
  --category Ritual --item "<omen English name>"

# 国服：current 使用当期接口，不传 season；历史赛季必须是 season_list 返回的确切 ID
python scripts/prices.py quote --realm cn --league current \
  --item "完美崇高石"
python scripts/prices.py quote --realm cn --league "<season_id>" \
  --category "通货" --item "崇高石"

# 指定统一单位（仅在有同服同赛季汇率时转换）
python scripts/prices.py quote --realm cn --league current \
  --item "完美崇高石" --unit d --e-per-d 200

# 同批次同类材料可以重复 --item；材料跨分类则多次调用（有本地缓存）
python scripts/prices.py quote --realm intl --league current --category Currency \
  --item "Chaos Orb" --item "Perfect Exalted Orb"

# 调试接口结构（不是报价）：
python scripts/prices.py snapshot --realm cn --league current
```

**注意：**命令中的 `--e-per-d 200` 是一个格式示例，**不是实时汇率**；真实运行必须从同服同赛季市场取数。

### 脚本经济数据契约

| 参数 | 要求 |
|---|---|
| `--realm intl` | 国际服只调用 `https://poe.ninja/poe2/api/economy/` |
| `--realm cn` | 国服只调用 `https://poecurrency.top/api/` |
| `--league current` | 国际服取 ninja leagues 第一赛季；国服 summary 省略 season 参数以获得当期赛季 |
| `--league <id>` | 严格匹配所选服务器的赛季目录；无效时拒绝报价 |
| `--category` | 国际服必须是 ninja 支持的分类；国服可按 `category_label` 过滤 |
| `--item` | 按该接口物品名称或 ID 精确匹配，可多次传入 |
| `--side sell` | **国服默认**使用最新卖 1 作为买入材料的参考，不代表一定成交 |
| `--side buy` | 国服买 1 参考，适合估计出售时残值，但不能和卖 1 直接互换 |
| `--unit` | 国际服利用同次快照参照通货价格换算；国服仅接受 c/e/d，并需验证同服汇率 |
| `--c-per-e, --e-per-d` | 国服不同计价单位的显式换算参数，来自本服该赛季（脚本不编造汇率） |
| `--refresh` | 忽略本地缓存；尊重社区 API 的低频限制 |
| `--fixture` | 离线测试 JSON，不联网；任何输出不能标为实时行情 |

JSON 输出包含市场/赛季/来源、时间戳及有效 `quotes`。`complete=false`时保留有效报价，并列出`missing`和`unusable`；退出码2仍表示整批不完整，完整成本未知。异常报价不进入quotes，不能读原始snapshot将其当有效或免费。

### 国际服：poe.ninja

文档：https://poe.ninja/docs/api

- 赛季：`GET /poe2/api/economy/leagues`
- 材料：`GET /poe2/api/economy/exchange/current/overview?league={id}&type={type}`
- PoE2 类别：`Currency, Fragments, Abyss, UncutGems, LineageSupportGems, Essences, SoulCores, Idols, Runes, Ritual, Expedition, Delirium, Breach, Verisium`。
- `lines[].primaryValue` **必须**按 `core.primary` 的单位理解；换单位时取同快照对价。
- 国际服接口使用**英文物品名称或稳定 ID**精确匹配。若用户只提供简体中文道具名，先从 poe2db 该道具英文页提取英文名，再运行 `--item`，不要凭空翻译或使用模糊子串。
- 有缓存；底层行情大约每小时更新。非官方保证成交价；轻量使用，遵守缓存、User-Agent 和限流。

### 国服：poecurrency.top

API 文档：https://poecurrency.top/api.html

- 赛季：`GET /api/season_list?version=poe2`，返回字符串数组。
- 当期：`GET /api/summary?version=2`，**不传 season**。
- 仅查询已归档历史赛季：`GET /api/summary?version=2&season={id}`。固定查询后**不会退回当前**。
- 响应为**按 category_label 分组**的 JSON 数组，每组有 `items[]`；物品字段包括 `item_name/engname/latest_sell1/latest_buy1/buy_avg/sell_avg/currency_unit/latest_datetime/error/error_info`。
- 每个物品自己的 `currency_unit` 可能是 `c/e/d`，**绝不能假设一个服务器的所有报价统一是 C 或 E**。
- 本站价格有 OCR 异常风险，脚本检测 `error=true` 会拒绝用于优化。站点提供需要 Token 的校验接口，但本脚本默认使用**公开的无需 Token 接口**。
- 服务方标注为个人非商业使用，商业部署前必须取得许可或更换合规数据来源。

## 4. 安全的成本比较

```text
第一步：查当前服务器、赛季的材料价格（记录单位、买卖方向）
第二步：统一币种；汇率只能从同服同赛季获得，缺汇率则要求补充或不比较
第三步：把预兆、品质补回、失败后清理、材料本身按是否每轮消耗分类
第四步：读取 poe2db 权重计算每种操作的本轮命中率
第五步：用条件期望比较路线，保留失败后的残值、修复方案与止损点
第六步：必要时从对应服交易市场核对成品/锁好词缀底材的真实挂单
```

**禁止**跨国服/国际服、跨赛季、跨价格单位直接相加。行情 API 失败时明确报缺价，不得偷偷用另一市场补。

## 紧凑取数

使用 `scripts/craft_math.py fetch` 一次提取页面嵌入JSON到本地；随后 pool 只输出匹配、目标与汇总。当前接口支持直接解析 new ModsView 的JSON，不需要探查JS资源或将网页全文注入对话。接口变化时报告具体缺项，保留本地原始文件再选择其他取数手段。价格按已确定市场批量 quote；snapshot仅供排查结构，零值/异常不得被当作免费报价。
