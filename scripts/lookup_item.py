#!/usr/bin/env python3
"""Search independent item effects and trigger relationships; no recipe selection."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def load_contracts():
    path = Path(__file__).resolve().parents[1] / 'references/item-contracts.json'
    return json.loads(path.read_text(encoding='utf-8'))['items']


WORDS = {
    'essence': ('精华', 'essence'), 'alloy': ('合金', 'alloy'),
    'prefix': ('前缀', '左旋', 'prefix', 'sinistral'),
    'suffix': ('后缀', '右旋', 'suffix', 'dextral'),
    'remove': ('删除', '移除', '删', 'remove', 'delete'),
    'add': ('增加', '新增', '添加', '生成', 'add', 'augment'),
    'quality': ('品质', '质量', 'quality', '催化剂', 'catalyst'),
    'maximum': ('最大', '上限', 'maximum', 'capacity', 'cap'),
    'fracture': ('分裂', '破裂', '锁词', 'fractur'),
    'preserve': ('保留', '保护', 'preserv', 'protect'),
    'desecrate': ('亵渎', '渎灵', 'desecrat'),
    'reveal': ('揭示', 'reveal'), 'reroll': ('重骰', '重投', '重掷', 'reroll'),
    'exalt': ('崇高', 'exalt'), 'chaos': ('混沌', 'chaos'), 'annul': ('剥离', 'annul'),
    'weight': ('权重', '概率', '几率', 'weight', 'chance'),
    'fire': ('火焰', '火', 'fire'), 'cold': ('冰霜', '冰', 'cold'),
    'lightning': ('闪电', '电', 'lightning'), 'physical': ('物理', 'physical'),
    'attack': ('攻击', 'attack'), 'caster': ('施法', 'caster', 'cast speed'),
    'speed': ('速度', 'speed'), 'life': ('生命', 'life'), 'mana': ('魔力', 'mana'),
    'armour': ('护甲', 'armour', 'armor'), 'evasion': ('闪避', 'evasion'),
    'energy_shield': ('能量护盾', 'energy shield'), 'attribute': ('属性', 'attribute'),
    'rarity': ('稀有度', 'rarity'), 'resistance': ('抗性', '抗', 'resistance'),
    'socket': ('插槽', '孔位', '孔', '镶嵌', 'socket'),
    'corrupt': ('腐化', 'corrupt'), 'sanctify': ('圣化', 'sanctif'),
    'bound': ('绑定', 'bound'), 'destroy': ('摧毁', '销毁', 'destroy'),
    'convert': ('转换', '转化', 'convert'),
    'ring': ('戒指', 'ring'), 'amulet': ('项链', 'amulet'), 'belt': ('腰带', 'belt'),
    'weapon': ('武器', 'weapon'), 'gloves': ('手套', 'gloves'), 'boots': ('鞋', 'boots'),
    'helmet': ('头盔', 'helmet'), 'jewel': ('珠宝', 'jewel'), 'waystone': ('引路石', 'waystone'),
    'magic': ('魔法', 'magic'), 'rare': ('稀有', 'rare'),
    'bone': ('骨', 'bone', 'jawbone', 'collarbone', 'rib', 'cranium', 'vertebrae'),
}


def alias_pattern(word):
    if not word.isascii():
        return re.escape(word)
    stem = word in ('fractur', 'desecrat', 'preserv', 'protect', 'exalt', 'annul', 'corrupt', 'sanctif', 'reveal')
    return r'(?<![a-z])' + re.escape(word) + (r'[a-z]*' if stem else r'(?:s|es)?') + r'(?![a-z])'


def concepts(text):
    body = text.casefold()
    return {key for key, words in WORDS.items() if any(re.search(alias_pattern(word), body) for word in words)}


def parse_query(query):
    # Consume longest aliases first so 属性 is not discarded as an unknown suffix
    # and matching "稀有度" doesn't accidentally demand the rarity "Rare".
    remaining = query.casefold()
    found = set()
    aliases = sorted(((word, key) for key, words in WORDS.items() for word in words),
                     key=lambda pair: len(pair[0]), reverse=True)
    for word, key in aliases:
        if re.search(alias_pattern(word), remaining):
            remaining = re.sub(alias_pattern(word), ' ', remaining)
            found.add(key)
    literal_terms = re.findall(r'[^\s,，;；+]+', remaining)
    return found, literal_terms


def effect_text(rec):
    return json.dumps([rec['name'], rec['target'], rec['state_effects'],
                       rec.get('description', []), rec.get('modifies', {})], ensure_ascii=False).casefold()


def search(items, name='', contains=False, category=None, query=None):
    if category:
        items = [x for x in items if category.casefold() in x['category'].casefold()]
    if name:
        items = [x for x in items if (name.casefold() in x['name'].casefold() if contains
                                      else name.casefold() == x['name'].casefold())]
    if query:
        wanted, literal = parse_query(query)
        items = [x for x in items if wanted <= concepts(effect_text(x)) and
                 all(term in effect_text(x) for term in literal)]
    return items


def compact(rec):
    keys = ('name', 'category', 'operation', 'action_family', 'target', 'state_effects',
            'preconditions', 'modifies', 'minimum_modifier_level', 'effect_coverage',
            'availability', 'fail_and_irreversibility', 'source_url', 'verification_level',
            'description_as_of', 'relation_evidence')
    out = {k: rec[k] for k in keys if k in rec}
    effects = rec.get('target_effects', [])
    out['description'] = [line for line in rec.get('description', [])
                          if line.partition(':')[0].strip() not in {x['target'] for x in effects}]
    if effects:
        out['target_effects'] = effects
    out['notes'] = rec['conflict_and_capacity']
    return out


def relations(rec, items):
    family = rec.get('action_family')
    if family:
        stages = [family] + (['desecrate_reveal'] if family == 'desecrate' else [])
        return {'modifiers': [compact(x) for x in items
                              if set(stages) & set(x.get('modifies', {}).get('families', []))],
                'scope': '触发关系；部位、输入状态、共同触发与名额仍按各项作用判断。'}
    change = rec.get('modifies', {})
    return {'applies_to_families': change.get('families', []),
            **({'requires_removable_side': change['delete_side']} if 'delete_side' in change else {})}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('name', nargs='?', default='', help='精确英文名；不知道名字用 --query')
    p.add_argument('--query', help='功能/对象关键词，所有条件共同匹配；不认识的词保留为文字条件')
    p.add_argument('--contains', action='store_true')
    p.add_argument('--category')
    p.add_argument('--limit', type=int, default=6)
    p.add_argument('--detail', action='store_true', help='完整原始记录')
    p.add_argument('--related', action='store_true', help='按操作触发关系返回修饰项')
    args = p.parse_args()
    if not (args.name or args.query or args.category):
        p.error('提供名称、--query 或 --category')
    all_items = load_contracts()
    matches = search(all_items, args.name, args.contains, args.category, args.query)
    rows = []
    for rec in matches[:max(1, args.limit)]:
        out = dict(rec) if args.detail else compact(rec)
        if args.related:
            out['related'] = relations(rec, all_items)
        rows.append(out)
    parsed, literal = parse_query(args.query or '')
    print(json.dumps({'matches': len(matches), 'shown': len(rows), 'truncated': len(matches) > len(rows),
                      'query_concepts': sorted(parsed), 'literal_terms': literal, 'items': rows}, ensure_ascii=False))
    if not matches:
        raise SystemExit('无本地匹配；文字条件未被丢弃。结果不证明游戏中不存在；可换术语或查询具体来源。')


if __name__ == '__main__':
    main()
