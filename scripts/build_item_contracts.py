#!/usr/bin/env python3
"""Generate a per-name *reference contract* from the checked name baseline.

This is deliberately NOT a static PoE2 modifier database: fields marked live_required
must be checked against current poe2db on the exact target item and game version.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'references'
CAT=json.loads((REF/'catalog-audit.json').read_text(encoding='utf-8'))
CURRENCY='https://poe2db.tw/us/Currency'
ESSENCE='https://poe2db.tw/us/Essence'
OMEN='https://poe2db.tw/us/Omen'
RUNE='https://poe2db.tw/us/Rune'
ABYSS='https://poe2db.tw/us/Abyss'
VAAL='https://poe2db.tw/us/Fate_of_the_Vaal'
CORR='https://poe2db.tw/us/Corrupted'
BREACH='https://poe2db.tw/us/Breach'
BASICS='https://poe2db.tw/us/Minimum_Modifier_Level'
SPECIAL='https://poe2db.tw/us/Modifiers'

items: dict[str,dict]={}

def add(name, category, operation, target, pre, effect, constraints, risk='一般消耗；依据具体道具核对', source='', audit='category_contract', **extra):
    if name in items: raise ValueError(f'duplicate {name}')
    rec=dict(name=name,category=category,operation=operation,target=target,preconditions=pre,
             state_effects=effect,conflict_and_capacity=constraints,fail_and_irreversibility=risk,
             source_url=source, verification_level=audit,
             live_required=['当前游戏版本及是否可取得','该装备当前状态下可否施加',
                            '当前具体装备部位的效果/词缀组与权重','单步和失败后的成本'])
    rec.update(extra)
    items[name]=rec

# Essence families. *Never* infer guaranteed mods from the name across grades/items.
for family in CAT['essence_base_families']:
    for grade in ('Lesser ', '', 'Greater ', 'Perfect '):
        name=f'{grade}Essence of {family}'
        is_perfect=grade=='Perfect '
        add(name,'Essence', 'rare_remove_one_force_add' if is_perfect else 'magic_to_rare_force_add',
            '仅限此品阶详情页明确列出的装备类型',
            ['Rare','有符合删除与新生成规则的词缀','允许添加 crafted，通常默认 1 条'] if is_perfect else
            ['Magic','仍可添加对应的 crafted 词缀','必须检查已占前后缀及 crafted 名额'],
            '随机删除一条词缀，然后生成该道具在该装备部位对应的固定 crafted 词缀' if is_perfect else
            '魔法升级稀有，并为当前装备部位增加规定的 crafted 词缀',
            ['同组/合金/现有 crafted 名额限制', '目标部位 guaranteed 词缀可能与同系列别的品阶完全不同',
             '删除端是否受结晶预兆约束需按当期验证'],
            '可能随机删除 B 的关键词缀；造成不可直接恢复的状态' if is_perfect else '稀有度升级后可能失去魔法专属制作窗口',
            ESSENCE, tier='perfect' if is_perfect else ('lesser' if grade=='Lesser ' else 'greater' if grade=='Greater ' else 'normal'))

for name in CAT['essence_special']:
    effect='稀有物品随机删除一条，添加此精华在当前装备部位的特殊 crafted 词缀'
    constraints=['必须核对目标装备类型具体保证词缀','crafted 名额和词缀组','结晶预兆如适用，仅按其描述更改删除端']
    if name=='Essence of the Breach':
        effect='在适用的 Jewellery 上随机删一条并保证添加 +20% to Maximum Quality crafted 前缀（在没有被其他词缀组阻挡的前提下）'
        constraints+=['移除此最大品质前缀本身不回退已存品质；释放前缀位和 crafted 名额，降低此后可添加上限',
                      '品质存续为用户确认及玩家制作记录，证据与版本边界见 references/advanced-interactions.md；不能无依据判为不可用 bug',
                      '催化预兆耗尽品质或更换品质类型后，不能无条件补回 40；重新提高上限要计入删词风险和费用',
                      '词缀等级由具体部位词缀数据提供，与装备需求等级分开']
    add(name,'Special Essence','rare_remove_one_force_add','当前道具详情列出的装备类型',['Rare','可用 crafted 名额','被删除词缀合法'],effect,constraints,
        '可能切到珍贵词缀；成功后仍需验证 crafted 与同组互斥',ESSENCE,
        audit='item_effect_reviewed' if name=='Essence of the Breach' else 'category_contract')
for name in CAT['alloys']:
    effect='从 Rare 装备中随机删除一条并添加该 Alloy 在当前部位保证的 crafted 复合词缀'
    note=['必须打开单件合金详情检查保证的前/后缀位置与数值','crafted 上限、共存的普通词缀组和操作前资格','不要假设先删后判断同组']
    if name=='Swift Alloy':
        effect='手套可保证施法速度后缀；戒指可保证攻击速度后缀；其他部位按实际详情'
        note+=['手套施速与普通攻速后缀存在用户实测冲突','同组冲突未验证之前不得将双速度写成可行']
    if name=='Sovereign Alloy':
        effect='武器可保证已镶嵌增幅器效果提高的 crafted 后缀；其它部位效果不同'
    if name=='Celestial Alloy':
        effect='武术武器可获得命中+局部攻击速度复合 crafted 前缀；其它部位效果不同'
    add(name,'Alloy','rare_remove_one_force_add','只适用该合金列出的装备类别',
        ['Rare','允许此 Alloy 的 guarantee mod','有相应 crafted 容量并满足同组限制'],effect,note,
        '随机删除可能破坏 A，且可能因现有同组而无法使用',ESSENCE,
        audit='item_effect_reviewed' if name in ('Swift Alloy','Sovereign Alloy','Celestial Alloy') else 'category_contract')

# Individual omen names: category metadata retained; trigger line needs live page check.
for category,names in CAT['omens'].items():
    for name in names:
        role='historical_unavailable' if '历史' in category else ('wearable_action_modifier' if '穿戴' in category else 'not_general_equipment')
        add(name,'Omen / Saga',role,'见单件详情中的下一次具体操作 / 装备或非装备对象',
            ['激活于背包','下一次匹配的具体通货或行为','检查能否与其他预兆同时触发'],
            '改写说明指定的触发行为；具体条件与效果见description',
            ['不要由左右旋名字臆造效果','不应把触发后总概率当成保底','检查是否属于历史不可获得项目'],
            '消耗触发预兆；某些条目可能导致圣化、腐化、整装重铸或不可逆改变',OMEN,
            availability='must_verify_current' if role!='historical_unavailable' else 'historical_do_not_assume_acquirable')

# Basic rune variants do not share fixed socket bonuses across tiers or target slots.
for name in CAT['runes']:
    if name=='Masterwork Rune':
        add(name,'Rune','upgrade_socketed_rune','须符合具体道具说明的已镶嵌符文及插槽',
            ['适用 Rune / 槽位','阅读当前原文','查询是否会改变 socket-bound/稀有度'],
            '提升指定镶嵌符文而非直接添加普通前后缀',
            ['不同类增幅器不一定都能被升级','需要确认目标能否被覆盖'],
            '不可回退的增幅器材料消耗；最终取出规则不同',RUNE)
    else:
        add(name,'Basic Rune','socket_augment','具有适配增幅孔的装备（具体受部位限制）',
            ['可用增幅孔','Rune 的装备/部位要求','当前腐化/圣化限制'],
            '对适用部位提供镶嵌效果，数值随品阶和部位改变；具体效果见description',
            ['查看是否 Socket-bound、类别限制、同名数量限制、套装/羁绊','被覆盖后原道具一般不返还','不会自行生成前后缀'],
            '覆盖损失旧 Rune，绑定时不能覆盖',RUNE)

levels={
    'Greater Chaos Orb':35,'Perfect Chaos Orb':50,
    'Greater Orb of Transmutation':44,'Perfect Orb of Transmutation':70,
    'Greater Orb of Augmentation':44,'Perfect Orb of Augmentation':70,
    'Greater Regal Orb':35,'Perfect Regal Orb':50,
    'Greater Exalted Orb':35,'Perfect Exalted Orb':50,
}
for name in CAT['currency_tab']:
    pre=['按具体通货说明的当前装备稀有度、空槽、腐化状态','必须核对道具描述']
    risk='会消耗道具并改变装备；以具体详情页判断是否不可逆'
    op='currency_specific'
    eff='按对应通货说明执行，不能从道具级别推断统一操作'
    constraints=['高级/完美的 Minimum Modifier Level 适用 R01/R02 例外规则','不允许无条件删除整个低阶词缀族']
    if 'Chaos Orb' in name:
        op='remove_one_add_one';pre=['Rare','随机删除 1 条可删词缀后，按剩余状态重新随机添加 1 条'];eff='先删一条、再加一条；新增端可能发生位置/互斥池变化';risk='可能删除锁之外的珍贵词缀'
        constraints+=['分裂词不参与删除；可与分裂组合，其他未分裂词仍可删；是否继续由当前池、费用与损失计算',
                      '不会保护其他未分裂好词，也不会自动增加词缀总数；普通池不能生成 crafted 或亵渎目标']
    elif 'Orb of Transmutation' in name:
        op='normal_to_magic_one_mod';pre=['Normal'];eff='普通→魔法，加 1 条随机词缀'
    elif 'Orb of Augmentation' in name:
        op='magic_add_one';pre=['Magic','有空的普通词缀槽'];eff='魔法装备增加 1 条词缀；通常最多1前缀和1后缀，已有单侧词时只能新增另一侧'
        constraints+=['新增不移除旧词；普通剥离不改变魔法稀有度，删除后按剩余侧别重算可新增池']
    elif 'Regal Orb' in name:
        op='magic_to_rare_add_one';pre=['Magic'];eff='魔法→稀有，增加 1 条词缀'
    elif 'Exalted Orb' in name:
        op='rare_add_one';pre=['Rare','至少有 1 个可用词缀槽'];eff='稀有装备增加 1 条词缀'
    elif name=='Orb of Alchemy':
        op='normal_or_magic_to_rare_4mod';pre=['Normal 或 Magic'];eff='升级稀有并得到 4 条随机词缀'
    elif name=='Orb of Annulment':
        op='remove_one';pre=['有 1 条可删词缀'];eff='随机删除一条词缀，物品稀有度不因此改变';risk='可能直接毁掉高价值词缀'
    elif name=='Fracturing Orb':
        op='fracture_random_eligible';pre=['Rare','至少 4 条显式词缀','候选中有可破裂词缀'];eff='永久固定一条符合条件的随机词缀';risk='选错后通常不能重新做原有高价词缀'
        constraints+=['可与混沌等操作组合，是否经济由具体状态计算；比较购买已有分裂胚和自制锁错损失',
                      '保护范围仅为分裂词；不能把其他词视为锁定，也不能默认目标特殊词可分裂']
    elif name=='Vaal Orb':
        op='random_corrupt';pre=['道具必须满足当前瓦尔宝珠要求'];eff='随机改变物品，并赋予 Corrupted';risk='腐化不可逆；可能阻止后续常规 crafting'
    elif name=='Hinekora\'s Lock':
        op='preview_next_currency';pre=['可应用于当前装备'];eff='预见下一次通货结果，任何中间修改会清除预见状态';risk='预见不是修改命中率；需要单独计算预言成本'
    elif name=='Orb of Chance':
        op='upgrade_to_unique_or_destroy';pre=['Normal'];eff='转为传奇或摧毁装备';risk='可能直接摧毁装备'
    elif name=='Divine Orb':
        op='reroll_explicit_values';pre=['有可重骰词缀'];eff='重骰现有词缀数值（特定预兆可能改为固有重骰/圣化）'
    elif name=='Mirror of Kalandra':
        op='mirror';eff='创造镜像装备';risk='高成本不可逆，镜像物品通常不能进一步修改'
    elif name in ('Blacksmith\'s Whetstone','Arcanist\'s Etcher','Armourer\'s Scrap','Glassblower\'s Bauble','Gemcutter\'s Prism'):
        op='increase_regular_quality';eff='提高适用物品品质，常规最大值与效果按装备类型核查'
    elif name=='Artificer\'s Orb':
        op='augment_socket';pre=['Martial Weapon、Wand、Staff 或 Armour','当前仍可添加 Augment Socket'];eff='给适用装备增加增幅孔；不是技能辅助孔'
    elif name.endswith(' Shard'):
        op='shard';eff='合成/兑换材料，不是对穿戴装备直接执行的 crafting 行为'
    elif name in ('Lesser Jeweller\'s Orb','Greater Jeweller\'s Orb','Perfect Jeweller\'s Orb'):
        op='skill_gem_socket_adjustment';pre=['Skill Gem 或带有自带技能的装备','当前辅助孔数量满足该品阶使用条件'];eff='增加技能辅助孔；0.5起也可用于装备自带技能，多个自带技能同时生效。不是装备增幅孔'
    if name in levels:
        pre.append(f'item level >= {levels[name]}，否则禁止使用')
        constraints.append(f'Minimum Modifier Level = {levels[name]}；整个词缀类型会消失时有保留例外')
    target = {
        'remove_one_add_one':'Rare item', 'normal_to_magic_one_mod':'Normal item',
        'magic_add_one':'Magic item', 'magic_to_rare_add_one':'Magic item',
        'rare_add_one':'Rare item', 'normal_or_magic_to_rare_4mod':'Normal / Magic item',
        'fracture_random_eligible':'Rare item',
        'skill_gem_socket_adjustment':'Skill Gem / equipment-granted Skills',
        'augment_socket':'Martial Weapon / Wand / Staff / Armour',
        'shard':'合成碎片；不是直接装备操作',
    }.get(op, '具体对象见原始description和preconditions')
    add(name,'Currency',op,target,pre,eff,constraints,risk,CURRENCY,
        audit='item_effect_reviewed' if name in levels or op!='currency_specific' else 'category_contract',
        minimum_modifier_level=levels.get(name))

vaal_overrides={
    'Core Destabiliser':('alter_soul_core','Soul Core',['已有 Soul Core'], '以不可预测方式改变 Soul Core','可能摧毁 Soul Core'),
    "Vaal Armourer's Infuser":('vaal_increase_over_quality','Armour',['品质 >= 20%','品质已达到当前有效 Maximum Quality（包括底材/词缀提供的额外上限）','物品当前可灌注'], '逐次提升品质；可超最大品质最多累计 +10%','有机会腐化并终止通常操作'),
    "Vaal Blacksmith's Infuser":('vaal_increase_over_quality','Martial Weapon',['品质 >= 20%','品质已达到当前有效 Maximum Quality（包括底材/词缀提供的额外上限）','物品当前可灌注'], '逐次提升品质；可超最大品质最多累计 +10%','有机会腐化并终止通常操作'),
    "Vaal Catalysing Infuser":('vaal_increase_over_quality','Ring / Amulet（不是 Belt）',['品质 >= 20%','品质已达到当前有效 Maximum Quality（包括底材/词缀提供的额外上限）','物品当前可灌注'], '逐次提升品质；可超最大品质最多累计 +10%','有机会腐化并终止通常操作'),
    "Vaal Arcanist's Infuser":('vaal_increase_over_quality','Wand / Staff / Sceptre',['品质 >= 20%','品质已达到当前有效 Maximum Quality（包括底材/词缀提供的额外上限）','物品当前可灌注'], '逐次提升品质；可超最大品质最多累计 +10%','有机会腐化并终止通常操作'),
    "Architect's Orb":('corrupted_modify_or_destroy','Corrupted Equipment / Jewel',['Corrupted'], '随机改变腐化装备或珠宝','可能直接摧毁物品'),
    "Ancient Infuser":('tablet_random_change_corrupt','Tablet',['碑牌'], '不可预测地改变碑牌并腐化','不可逆腐化，非普通穿戴装备做装'),
    "Orb of Extraction":('destroy_item_refund_eligible_augments','Equipment',['装备中存在可提取且非 Socket-bound 增幅器'], '销毁整件装备以返回非 Socket-bound 增幅器','**必定销毁装备**；不可当免费拆卸'),
    "Crystallised Corruption":('corrupted_skill_gem_modify_or_destroy','Corrupted Skill Gem',['Corrupted Skill Gem'], '随机改变已腐化技能宝石','可能摧毁技能宝石，不作用穿戴装备'),
    "Vaal Cultivation Orb":('modify_corrupted_unique','Vaal Unique / other Unique',['Unique','需查是哪一种传奇'], '腐化瓦尔传奇最多改 2 条词缀；其他传奇变同类别腐化传奇','不可逆且结果随机'),
    "Vaal Siphoner":('corrupted_rare_jewelry_on_kill','Corrupted Rare Jewellery',['Corrupted','Rare','必须满足击杀计数条件'], '到击杀门槛后随机一条词缀降阶，其他词缀的数值在当前值到普通最大值+10%的范围内改善；详见 Keywords 的 Vaal Siphoner 说明', '随机降阶可能损坏目标；不是删除一词或腾出词缀位'),
    "Sacrificial Regalia":('item_base','Body Armour',['它是底材而非一次性通货'], '提供特定固有与基础属性','错误将底材当做可点击道具'),
}
for name in CAT['fate_of_vaal']:
    if name in vaal_overrides:
        op,target,pre,effect,risk=vaal_overrides[name]
        add(name,'Fate of the Vaal',op,target,pre,effect,
            ['每次发生腐化/销毁的后续可继续性','适用物品类别','在路线中的先后顺序'],risk,VAAL,
            audit='item_effect_reviewed')
    else:
        add(name,'Ancient Augment','socket_ancient_augment','当前名称列明的装备部位',
            ['装备对应部位有合适插槽','适用该 Ancient Augment 与数量限制'],
            '按手套/头盔/胸甲/鞋等具体部位赋予特有功能（不是重骰普通词缀）',
            ['Limited to 1 Ancient Augment','是否 Socket-bound、可否覆盖均需逐件核对'],
            '安装后有插槽占用和可能的覆盖成本',VAAL)

for name in CAT['abyss_bones']:
    slot = 'Weapon / Quiver' if name.endswith('Jawbone') else ('Armour' if name.endswith('Rib') else ('Jewellery' if name.endswith('Collarbone') else ('Jewel' if name.endswith('Cranium') else 'Waystone')))
    pre=['Rare','尚有亵渎容量','具体装备类别符合该骨头的使用目标']
    if name.startswith('Gnawed'):pre.append('item level <= 64')
    if name.startswith('Ancient'):pre.append('Minimum Modifier Level 40，需核对当前物品 ilvl 与特定例外')
    add(name,'Abyss Bone','add_unrevealed_desecrated',slot,pre,
        '增加待揭示亵渎词缀；后续由对应揭示机制产生该部位特殊池中的效果'+('；此骨有机会生成 otherworldly modifiers，具体池与概率另查' if name=='Altered Collarbone' else ''),
        ['不等于普通前后缀抽词','亵渎名额与已存在 crafted 分开核查','破裂概率按合格候选计数'],
        '可能消耗亵渎名额并阻断未来亵渎；特殊预兆可能有腐化后果',ABYSS)

# Additional equipment-crafting-relevant systems outside the six counted taxonomies.
for name,target in [
    ("Yaomac's Orb of Sacrifice",'Rare Weapon / Quiver'),
    ("Kopec's Orb of Sacrifice",'Rare Armour'),
    ("Kamasa's Orb of Sacrifice",'Rare Ring / Amulet / Belt'),
    ("Yugul's Orb of Sacrifice",'Rare Jewel')]:
    add(name,'Sacrifice Orb','upgrade_corruption_enchantment_remove_random_mod',target,
        ['Rare','有对应 Corruption Enchantment','目标物品可以接受该献祭道具'],
        '升级腐化附魔，同时随机移除一条词缀',
        ['不能保证只移除普通废词','确认腐化状态、附魔等级与后续可继续性'],
        '不可逆切掉珍贵词缀，需计失败胚残值',CORR,audit='item_effect_reviewed')
for name,effect in [
    ('Blazing Flux','现有冰霜、闪电抗性词缀→等价火抗'),
    ('Chilling Flux','现有火焰、闪电抗性词缀→等价冰抗'),
    ('Crackling Flux','现有火焰、冰霜抗性词缀→等价电抗'),
    ('Void Flux','现有火焰、冰霜、闪电抗性词缀→等价混沌抗性')]:
    add(name,'Resistance Flux','convert_existing_resistance','有可转换抗性词缀的物品',
        ['持有匹配源抗性词缀','查目标等价阶级与词缀组'], effect,
        ['可能转换所有符合条件的抗性词缀，不只是其中一条','要与 Aldur 的武器元素词缀转换分开'],
        '可能永久改变原本需要保留的抗性词缀', 'https://poe2db.tw/us/Resistance',audit='item_effect_reviewed')
for name,target in [('Passion of Aldur','Fire'),('Breath of Aldur','Cold'),('Ire of Aldur','Lightning'),('Betrayal of Aldur','Chaos')]:
    add(name,'Aldur Rune','socket_bound_transform_elemental_mods','Weapon',
        ['武器增幅孔','可接受永久 Socket-bound', '需要存在可转换的源元素词缀'],
        f'把现有其他元素词缀转换为等价 {target} 词缀（逐项核对源元素范围）',
        ['Socket-bound：永久占孔，不得覆盖/抽取','不是简单的抗性 Flux'],
        'Socket-bound 永久锁死孔位、词缀转换的结果必须校验共存性',SPECIAL,audit='item_effect_reviewed')
for name,effect,bind in [
    ("Astrid's Creativity",'增加 1 条可拥有的 Crafted Modifier 名额',False),
    ("Serle's Triumph",'改变后缀容量，允许多一条后缀',True),
    ("Thrud's Might",'解锁特殊武器可生成词缀池',True),
    ("Cadigan's Epiphany",'对手套镶嵌结构进行改变，产生珠宝孔等专属效果',True)]:
    add(name,'Meta Augment','socket_augment_meta','对应装备类型，具体详情核对',
        ['目标装备有可用增幅孔','读取该增幅器具体适用部位与等级'],effect,
        [('Socket-bound: 不可覆盖' if bind else '非 Socket-bound：可覆盖，但后续 crafted 存续需核实'),
         '现有/最终装备所有词缀名额、插槽名额与源限制需重算'],
        '可能改变整个后续做装可行性与永久孔位结构',RUNE,
        audit='item_effect_reviewed' if name in ("Astrid's Creativity","Serle's Triumph","Thrud's Might") else 'category_contract')
# Pool-unlocking Socket-bound runes and unique-destroying rune production.
# These are frequently missed by an otherwise exhaustive ordinary-currency catalog.
for name,target,pool in [
    ("Uhtred's Sidereus",'Boots','Chronomancy'),
    ("Kolr's Hunt",'Gloves','Marksman'),
    ("Vorana's Carnage",'Helmet','Berserking'),
    ("Medved's Tending",'Body Armour','Soul'),
    ("Katla's Gloom",'Gloves','Decay'),
]:
    add(name,'Pool-Unlocking Rune','socket_bound_unlock_modifier_pool',target,
        ['适用装备已有可用 Augment Socket','允许不可替换的永久 Socket-bound',
         'Limited to 1；在生成特殊词缀之前必须先装入'],
        f'安装后允许该部位在后续制作中生成 {pool} 类型的特殊词缀；安装本身不会生成词缀',
        ['Socket-bound：不可移除/覆盖/抽取','须核对新解锁词缀的合法等级、权重与既有组冲突',
         'Bonded 效果需满足独立触发条件'],
        '永久失去可替换增幅孔；可能排除其它最终增幅器方案',
        'https://poe2db.tw/us/Socket-bound_Augments',audit='item_effect_reviewed')
add("Aldur's Legacy",'Rune Production','destroy_unique_create_legacy_rune','Unique Kalguuran / Ezomyte Equipment',
    ['目标为合格的 Kalguuran 或 Ezomyte 传奇装备','有合法 Augment Socket',
     '使用前明确知晓原传奇会被销毁'],
    '嵌入后销毁原传奇，并生成承载对应传奇能力的 Legacy Rune',
    ['不能一边保留原传奇 B 一边通过此道具抽取它的效果',
     '后续生成的 Legacy Rune 须查具体部位效果与 Bonded 条件'],
    '**必定销毁原传奇装备**；仅在放弃原装备或以产物符文为 B 时使用',
    'https://poe2db.tw/us/Expedition',audit='item_effect_reviewed')

for name in ['Breach Ring','Refined Breach Ring']:
    add(name,'Special Jewellery Base','item_base','Ring',['是底材，不是可点击货币'],
        '+20% Maximum Quality 底材固有' if name=='Breach Ring' else '+25% Maximum Quality（以该底材原文复核）',
        ['品质固有来源与 crafted Essence of the Breach 来源不同','物品部位限定'],
        '原有 A 若不是此底材，无法靠普通 C 把它变为该底材',BREACH,
        audit='item_effect_reviewed' if name=='Breach Ring' else 'category_contract')
for name in ['Penumbra Ring','Tenebrous Ring','Penumbra Amulet','Tenebrous Amulet']:
    add(name,'Special Jewellery Base','item_base_extra_affix_capacity','Ring/Amulet',
        ['是底材，不是一次性通货'],
        '+2 前缀容量，-2 后缀容量' if name.startswith('Penumbra') else '-2 前缀容量，+2 后缀容量',
        ['容量变化影响封锁、随机池、目标可共存性','必须检查特定版本基础词缀'],
        '无法把其他现成底材用普通 C 转成此底材',SPECIAL,audit='item_effect_reviewed')
add('Perfect Flux','Expedition Currency','raise_item_inherent_skill_level','带有适用装备技能的道具',
    ['当前物品符合 Perfect Flux 的使用条件','检查是否需要最低等级/特殊源'],
    '将物品自带技能提升到 20 级（准确适用列表以当期原文为准）',
    ['与 Blazing/Chilling/Crackling/Void 的抗性转换完全不同'],
    '高价值终局资源，检查是否真正作用于 B 的固有技能','https://poe2db.tw/us/Perfect_Flux')
# Catalyst families are a dynamic target/tag matrix. A few are found in the Breach site
# but do not treat suffixing 'Refined' as proof of live acquisition.
catalyst_tags={'Flesh':'Life','Neural':'Mana','Carapace':'Armour/Evasion/Energy Shield',"Uul-Netol's":'Physical',"Xoph's":'Fire',"Tul's":'Cold',"Esh's":'Lightning',"Chayula's":'Chaos','Reaver':'Attack','Sibilant':'Caster','Skittering':'Speed','Adaptive':'Attribute','Necrotic':'Minion'}
for f in catalyst_tags:
    for prefix in ('','Refined '):
        name=f'{prefix}{f} Catalyst'
        add(name,'Catalyst', 'apply_jewel_quality' if prefix else 'apply_jewelry_quality',
            'Jewel / other special applicable target' if prefix else 'Ring / Amulet',
            ['对应目标可接受此类品质','检查最大品质容量、当前其他品质类型'],
            f'添加或替换 {catalyst_tags[f]} 标签品质；该标签对目标具体词缀是否有效必须按原文核实',
            ['不同 Catalyst 类型通常相互替换','权重放大需要有效触发预兆且不保证目标'],
            '更换品质类型消耗已投入品质，催化预兆可能一次吃掉全部品质',BREACH,
            audit='category_contract')

# Searchable operation relations, not ordered crafting recipes.
for rec in items.values():
    name, category = rec['name'], rec['category']
    family = ('perfect_essence' if name.startswith('Perfect Essence') else
              'corrupted_essence' if category == 'Special Essence' else
              'essence' if category == 'Essence' else
              'alloy' if category == 'Alloy' else
              'chaos' if 'Chaos Orb' in name else
              'exalt' if 'Exalted Orb' in name else
              'regal' if 'Regal Orb' in name else
              'alchemy' if name == 'Orb of Alchemy' else
              'divine' if name == 'Divine Orb' else
              'chance' if name == 'Orb of Chance' else
              'augment' if 'Orb of Augmentation' in name else
              'transmute' if 'Orb of Transmutation' in name else
              'annul' if name == 'Orb of Annulment' else
              'desecrate' if category == 'Abyss Bone' else None)
    if family:
        rec['action_family'] = family

for side, word in [('Sinistral', 'prefix'), ('Dextral', 'suffix')]:
    for suffix, families, change in [
        ('Crystallisation', ['perfect_essence', 'corrupted_essence', 'alloy'], 'delete_side'),
        ('Erasure', ['chaos'], 'delete_side'),
        ('Annulment', ['annul'], 'delete_side'),
        ('Exaltation', ['exalt'], 'add_side'),
        ('Coronation', ['regal'], 'add_side'),
        ('Necromancy', ['desecrate'], 'add_side'),
    ]:
        rec = items.get(f'Omen of {side} {suffix}')
        if not rec:
            continue
        rec['modifies'] = {'families': families, change: word}
        if suffix == 'Crystallisation':
            rec['conflict_and_capacity'].append(
                '合金联动由 PoE2Wiki Alloy 的明确说明及玩家记录支持；不是由 crafted 标签推断。'
                'https://www.poe2wiki.net/wiki/Alloy；精华触发原文见 https://poe2db.tw/us/Omen')

items['Omen of Whittling']['modifies'] = {'families': ['chaos'], 'delete_selector': 'lowest_mod_level'}
items['Omen of Catalysing Exaltation']['modifies'] = {'families': ['exalt'], 'weights': 'catalyst_tag', 'consumes': 'all_catalyst_quality'}
items['Omen of Light']['modifies'] = {'families': ['annul'], 'delete_selector': 'desecrated'}
for name in CAT['abyss_bones']:
    items[name]['conflict_and_capacity'].append('通常同时最多一条亵渎词，不等于一生只能亵渎一次；移除后可再次亵渎。满词时的删除规则按具体骨头/预兆核对')
    items[name]['conflict_and_capacity'].append('待揭示亵渎词在Well of Souls（灵魂之井）揭示。各选项的生成/保证规则不能由候选池大小直接推算。https://poe2db.tw/us/Desecrated_Modifiers')

# Describe each modifier's independent trigger and changed part, not a sequence.
changes = {
    'Omen of Sinistral Alchemy': (['alchemy'], {'generation_constraint': 'maximum_prefix_count'}),
    'Omen of Dextral Alchemy': (['alchemy'], {'generation_constraint': 'maximum_suffix_count'}),
    'Omen of Greater Exaltation': (['exalt'], {'add_count': 2}),
    'Omen of Greater Annulment': (['annul'], {'remove_count': 2}),
    'Omen of Homogenising Exaltation': (['exalt'], {'generation_type': 'same_as_existing_modifier'}),
    'Omen of Homogenising Coronation': (['regal'], {'generation_type': 'same_as_existing_modifier'}),
    'Omen of the Blessed': (['divine'], {'reroll_scope': 'implicit'}),
    'Omen of Sanctification': (['divine'], {'result_state': 'sanctified', 'requires': 'rare'}),
    'Omen of Chance': (['chance'], {'outcome_constraint': 'avoid_destroy'}),
    'Omen of the Ancients': (['chance'], {'result': 'guaranteed_unique_same_class'}),
    'Omen of Abyssal Echoes': (['desecrate_reveal'], {'reroll_reveal_options': True}),
    'Omen of the Sovereign': (['desecrate'], {'guaranteed_family': 'Ulaman', 'target': 'Weapon / Jewellery'}),
    'Omen of the Liege': (['desecrate'], {'guaranteed_family': 'Amanamu', 'target': 'Weapon / Jewellery'}),
    'Omen of the Blackblooded': (['desecrate'], {'guaranteed_family': 'Kurgal', 'target': 'Weapon / Jewellery'}),
    'Omen of Putrefaction': (['desecrate'], {'replace_scope': 'all_modifiers', 'add_count': 'up_to_6_unrevealed', 'result_state': 'corrupted'}),
}
for name, (families, change) in changes.items():
    items[name]['modifies'] = {'families': families, **change}
for name in ('Omen of Homogenising Exaltation', 'Omen of Homogenising Coronation'):
    items[name]['availability'] = 'standard_only_exchange_since_0.5'
    items[name]['conflict_and_capacity'].append('0.5官方补丁：只在Standard货币交易出现，不作为当期赛季普遍可获得候选。https://www.pathofexile.com/forum/view-thread/3932540')
for side in ('Sinistral', 'Dextral'):
    items[f'Omen of {side} Crystallisation']['relation_evidence'] = {
        'alloy': {'status': 'confirmed_in_user_context', 'scope': '0.5制作语境的合金删除侧',
                  'support': ['https://www.poe2wiki.net/wiki/Alloy'],
                  'note': '用户确认已验证；预兆摘要仅写精华，不构成合金不能触发的反证。删除侧约束不等于保证添加侧或指定某条词。'}}
items['Essence of the Abyss']['conflict_and_capacity'].append('Mark of the Abyssal Lord：亵渎带此标记的装备时，必定移除标记并替换为更高tier的待揭示亵渎词；不是普通池抽词。https://poe2db.tw/us/Mark_of_the_Abyssal_Lord')
items['Fracturing Orb']['conflict_and_capacity'].append('被固定的词仍占槽位，通常不能移除或改动（包括数值）；特殊操作例外需有对应依据。https://poe2db.tw/us/Fractured_Modifiers')
items['Omen of Sanctification']['conflict_and_capacity'].extend([
    '0.5圣化按当前词缀数值乘倍率，不先重掷普通范围；输出依赖当前数值。https://www.pathofexile.com/forum/view-thread/3932540',
    '同一件装备只能圣化一次；圣化后无法再改变，不能再神圣重骰或再次圣化。当前0.5语境由用户确认。'])
items['Vaal Siphoner']['conflict_and_capacity'].append('Keywords的详细Vaal Siphoner说明明确是降tier并改善其余数值，短描述siphons不是删除空位的证据。https://poe2db.tw/us/Keywords')

# Extracted descriptions supply the actual per-item/per-target effects. The
# source text is not evidence of hidden selection order or game click testing.
descriptions = json.loads((REF/'item-descriptions.json').read_text(encoding='utf-8'))['items']
for rec in items.values():
    source = descriptions.get(rec['name'])
    rec['effect_coverage'] = 'source_description' if source else 'category_only'
    if source:
        rec['description'] = source['description']
        rec['description_as_of'] = source['as_of']
        rec['description_source'] = source['source_url']
        rec['target_effects'] = []
        for line in source['description']:
            match = re.match(r'^([^:]{1,80}):\s*(.+)$', line)
            if match and not match[1].startswith(('Minimum Modifier', 'Limited to', 'Stack Size', 'Requirements')):
                rec['target_effects'].append({'target': match[1].strip(), 'effect': match[2]})
        if rec['target_effects']:
            rec['target'] = list(dict.fromkeys(x['target'] for x in rec['target_effects']))
        rec['source_url'] = source['source_url']
        if rec['category'] == 'Omen / Saga':
            rec['state_effects'] = ' '.join(source['description'])
items['Omen of Putrefaction']['fail_and_irreversibility'] = '替换全部词缀并腐化；会损失现有目标和通常后续制作资格'
sanctification = items['Omen of Sanctification']
sanctification['target'] = '尚未圣化的 Rare item'
sanctification['preconditions'] = ['激活于背包', '下一颗 Divine Orb 用于尚未圣化的 Rare item']
sanctification['modifies'].update(requires='rare_and_not_sanctified', result_modifiable=False,
                                repeatable_on_same_item=False)
sanctification['state_effects'] += '；圣化为同件一次性终态，结果装备无法再改变。'
sanctification['fail_and_irreversibility'] = '圣化后无法修改或再次圣化；结果未达标也不能在原件上重骰修复，数值调整在圣化前完成。'
sanctification['verification_level'] = 'item_effect_reviewed'
sanctification['live_required'] = ['版本变化时复核圣化终态规则', '当前物品是否已经圣化',
                                   '圣化倍率分布与满足数值目标的概率', '当前市场材料价格']
sanctification['relation_evidence'] = {
    'sanctified_state': {'status': 'confirmed_in_user_context', 'scope': '0.5同件一次圣化及圣化后不可改变',
                         'note': '用户本轮明确确认；腐化专用通货的可修改性不外推到圣化物品。'}}

output={'schema_version':1,'audited_at':'2026-10-22',
        'scope':'274 verified-directory-name baseline plus additional mechanism-index names; category-contracts not item-by-item numeric validation',
        'read_first':'references/critical-rules.md',
        'warning':'verification_level=category_contract is not a live per-item verification. Reuse verified same-version effects; check the exact source for unresolved applicability or version differences.',
        'items':sorted(items.values(),key=lambda a:(a['category'],a['name']))}
p=(REF/'item-contracts.json')
p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Generated {len(items)} per-item contracts to {p} ({p.stat().st_size:,} bytes)')
from collections import Counter
print(Counter(i['category'] for i in items.values()))
