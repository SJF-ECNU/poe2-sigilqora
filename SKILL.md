---
name: poe2-sigilqora
description: 用流放之路2的基础机制、具体道具作用和概率成本，自主推导装备制作候选。适用于新胚制作、现物改装和下一步操作选择。
---

# PoE2 制作知识与计算

由当前装备与目标推导方案。中间状态、动作顺序和保护投入都是决策结果；知识提供实际机制、可组合手段和计算条件。

## 制作规划入口

规划比较的是**从当前状态到同一目标的选择**。用户改变某个中间状态或提出另一种起手时，从该状态重新选择后续动作；已有方案中的顺序、删除次数、保护方式和恢复费用都是可变的决策。讨论中的起点与目标沿用上下文，不把“已有锚点后的下一步”改解成“重新取得锚点”。

候选动作由**基础操作的品阶及适用修饰**共同组成：删除集合、生成侧/来源、权重和数量的变化会改变同一操作的损失与费用。普通/高级/完美C或追加各有输入资格、生成池和单价，按当前状态分别算；先C取词等手段的可行性不等于成本优势。已有好词时，按可用选择器重算可删集合与必须保留集合是否相交，再判断保护代价；裸操作的风险不能代替修饰后操作的风险。取得有价值中间状态也可购买，按实际买价、清理和续做费用比较。

制作规划先读 [通用做装知识合集](references/crafting-handbook.md)；其中是可按状态组合的手段，A/B表示任意目标词。候选取舍先保留影响决策的状态与费用，再对有竞争力的方案展开具体流程和计算。固定方案的模拟或精确期望只评价该方案；替代候选的后继尚未比较时，结论范围停留在“该方案的费用”。策略比较见 [crafting-logic.md](references/crafting-logic.md)。

合集已给常用原理与适用条件；已读事实、类别池和本市场报价继续复用。每次取数围绕一个影响选择的缺项，输出其相关字段；同类独立查询可批量处理。合法候选形成后，获取足以区分候选的报价或计算临界价；市场未知时先给条件成本，避免同时展开多市场全表。概率/行情仍有近似时，先给条件比较，精细分位数或更多模拟按实际需要补充。

## 基础机制

`references/state-and-planning.md` 定义稀有度/容量、词缀来源/组/标签、等级/阶级/数值、品质、插槽和特殊状态。它们决定操作资格和后继状态。魔法与稀有有不同容量及可用通货；最终稀有度不要求所有词都在该状态取得。分裂、定向删除、满位和互斥各自影响不同集合。来源的同时占用、历史使用和结果存续分别判断。

把操作理解为输入条件、删除选择器、生成来源/权重、容量变化和效果存续。针对目标差异寻找变化，再看哪些独立操作可构造前提或改变副作用。保留用户已有资产与硬需求，按实际后继状态比较成本。

## 查具体作用

```bash
python scripts/lookup_item.py --query '品质 火'
python scripts/lookup_item.py --query '删除 后缀' --related
python scripts/lookup_item.py '英文道具名' --related
```

查询共同匹配所有条件；未识别词保持文字条件并显示，不静默忽略。道具数据由查询器从 `references/item-contracts.json` 按需读取。紧凑结果包含适用对象、部位效果、输入、风险、原始描述和来源；`--detail`给完整记录。`--related`按触发操作/阶段找修饰项，并非制作顺序或联合生效保证。`effect_coverage=category_only`表示缺具体原文；`source_description`表示已有提取说明，不代表隐藏选择顺序或游戏点击已核实。

同版本、同条件已核实的机制可直接复用。证据按具体断言和范围使用；摘要省略某种联动不是已验证关系的反证。真正矛盾才核对条件和版本，保留未知边界。见 `references/compatibility-and-evidence.md`；已知部位冲突见 `references/known-conflicts.json`；具体不可逆风险见 `references/critical-rules.md`，存续/特殊选择器见 `references/advanced-interactions.md`。

## 取池与计算

```bash
python scripts/craft_math.py fetch --url 'https://poe2db.tw/us/装备类别或底材' --save /tmp/mods.json
python scripts/craft_math.py pool --file /tmp/mods.json --ilvl 等级 --find '效果关键词'
python scripts/craft_math.py pool --file /tmp/mods.json --ilvl 等级 --side prefix --target '家族@等级'
```

取一次类别池留在本地，底材页可按其类别链接回退。查效果默认跨来源，完整阶级覆盖与当前ilvl可用项分开；截断不等于更高阶不存在。选定来源后再算池；`pool`支持互斥组、最低等级（Minimum Modifier Level）、标签倍率。发现结果与本次可生成结果分开，无选侧模型时只有权重占比。最低等级整类例外按group近似处理，输出其条件边界。

`delete --file state.json` 输入当前 `rarity`、`mods`（id/side/fractured/protected/mod_level）及特殊 `caps`，可用`--side`、`--lowest-level`、`--add-side`计算删除分支及删后空位。`expect --probability P --roll C --reset R`仅适用于失败回到相同状态的循环。

一般概率与成本按不同后继状态递推，包含误删、恢复、重启、品质消耗、材料及残值；未知选侧/倍率/行情可用变量计算临界条件。定义和公式见 `references/crafting-logic.md`，不从单词缀概率拼整件总价。

价格用 `scripts/prices.py`，默认工作区缓存。市场/赛季未知时先给条件费用；部分报价只支持已知部分的计算，缺价/异常保持未知。取数入口见 `references/data-sources.md`。功能索引为 `references/mechanism-checklist.md`；目录与覆盖边界见 `references/catalog-index.md`、`references/material-audit.md`。这些按缺项查阅即可。

给出可执行操作、选择依据、关键分支和成本条件；用户提供新物品结果后按实际状态重算。
