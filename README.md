# Sigilqora · PoE2 装备制作推导 Skill

A knowledge-and-calculation skill for reasoning about Path of Exile 2 item upgrades.

让 Agent 根据装备当前状态、目标词缀与材料价格，推导可行操作并比较成本。包含基础机制、通用做装知识、道具作用检索、词缀池计算和国服／国际服报价工具。

## 能做什么

- 查清道具的适用条件、删除与新增效果、预兆触发关系和不可逆后果。
- 组合魔法阶段取词、分裂与亵渎垫锁、锁+C、定侧、占位、保证词和临时品质等手段。
- 将通货品阶和适用预兆作为候选参数，按删后状态、合法词池、失败恢复与后续费用计算。
- 比较自制、购买底材和半成品的完整费用；缺少数据时保留变量与适用边界。

这些手段的使用顺序由当前状态与成本决定。仓库提供知识和局部计算工具，完整方案仍由调用 Skill 的 Agent 推导。

## 安装

需要 Python 3.11 或以上；脚本仅使用 Python 标准库。查询词缀池和实时行情需要联网。

在 DeepSeek Harness 的项目根目录执行：

```bash
git clone https://github.com/SJF-ECNU/poe2-sigilqora.git .dsh/skills/poe2-sigilqora
```

其他支持本地 `SKILL.md` 的 Agent，可将仓库克隆到其技能目录，保持仓库内相对路径。已安装旧版时，先备份并停用旧技能目录，避免同时加载两个版本。

更新：

```bash
git -C .dsh/skills/poe2-sigilqora pull --ff-only
```

## 使用

向 Agent 提供物品类型或物品文本、目标词缀／阶级、必须保留的属性，以及有预算需求时的服务器、赛季与预算。入口是 [SKILL.md](SKILL.md)，通用手段见 [做装知识合集](references/crafting-handbook.md)。

在仓库目录也可直接使用工具：

```bash
python3 scripts/lookup_item.py --query '删除 后缀' --related
python3 scripts/craft_math.py fetch --url https://poe2db.tw/us/Rings --save /tmp/rings.json
python3 scripts/craft_math.py pool --file /tmp/rings.json --ilvl 75 --find 'Rarity'
python3 scripts/prices.py leagues --realm intl
python3 scripts/prices.py leagues --realm cn
```

计算参数、报价单位与异常处理见 [数据入口](references/data-sources.md) 和各脚本的 `--help`。通货行情与装备挂单是不同数据，缺价不能按免费处理。

## 目录与检查

| 路径 | 内容 |
|---|---|
| `SKILL.md` | Agent 入口 |
| `references/` | 机制、通用手段、道具记录及来源 |
| `scripts/` | 检索、词缀池、删除分支和报价工具 |
| `tests/` | 离线工具测试与合成报价数据 |

制作任务答案、个人会话、DSH 配置和实时行情缓存不随仓库发布。

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_catalog.py
```

测试验证工具计算、查询和数据处理，不能替代游戏内验证或真实 Agent 会话评估。脚本和 GitHub Actions 均不运行 DSH、不调用模型 API。

## 版本与证据

当前知识以 PoE2 **0.5** 制作语境整理，道具说明快照日期为 **2026-10-22**。记录区分游戏提取文本、官方补丁、玩家记录和已确认的实际联动，具体边界见 [覆盖说明](references/material-audit.md)。新补丁、隐藏选择规则、近似权重和市场变化可能影响计算；本项目不保证 Agent 总能找到最低成本方案，也未宣称 token 开销已获改善。

欢迎通过 Issue 或 PR 提供可复核的纠错：附游戏版本、装备状态、具体道具／词缀及来源或操作结果。保留证据范围，便于区分规则变化和计算错误。

## 许可与来源

本项目原创代码及原创说明采用 [MIT](LICENSE)。从 PoE2DB 等来源引用或整理的第三方文本保留上游许可，不因本仓库的 MIT 许可而改变；详见 [第三方资料说明](THIRD_PARTY_NOTICES.md)。游戏名称、文本及相关权利属于各自权利人，本项目为独立社区工具。
