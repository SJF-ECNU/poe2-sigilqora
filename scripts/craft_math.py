#!/usr/bin/env python3
"""Read-only local crafting arithmetic. It evaluates inputs, never chooses a recipe."""
from __future__ import annotations
import argparse
import datetime as dt
import html
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin


def read_data(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return data.get('data', data)


def fetch_pool(url, destination):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, timeout=25) as response:
        page = response.read(8_000_000).decode('utf-8')
    marker = page.find('new ModsView(')
    if marker < 0:
        category = re.search(r'<a\b[^>]*class=[\"\'][^\"\']*ItemClasses[^\"\']*[\"\'][^>]*href=[\"\']([^\"\']+)', page)
        if category:
            category_url = urljoin(url, html.unescape(category[1]))
            if category_url != url:
                result = fetch_pool(category_url, destination)
                result['base_page'] = url
                result['note'] = '已转到页面标明的装备类别词缀池；具体底材的特殊限制仍单独适用。'
                return result
        raise ValueError('页面没有词缀池；请使用装备类别页 / ModifiersCalc，不是物品介绍页。空结果不代表该词不存在。')
    start = page.find('{', marker)
    data, _ = json.JSONDecoder().raw_decode(page[start:])
    envelope = {'source': url, 'fetched_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'data': data}
    Path(destination).write_text(json.dumps(envelope, ensure_ascii=False), encoding='utf-8')
    return {'saved': destination, 'source': url,
            'sections': {k: len(v) for k, v in data.items() if isinstance(v, list) and v}}


def normalize(row):
    result = {
        'name': html.unescape(re.sub('<[^>]+>', '', row.get('Name', row.get('name', '')))),
        'level': int(row.get('Level', row.get('level', 0))),
        'side': {'1': 'prefix', '2': 'suffix'}.get(str(row.get('ModGenerationTypeID')), row.get('side')),
        'groups': row.get('ModFamilyList', row.get('groups', [])),
        'weight': float(row['DropChance'] if 'DropChance' in row else row['weight']),
        'text': html.unescape(re.sub('<[^>]+>', '', row.get('str', row.get('text', '')))),
        'tags': row.get('tags', re.findall('data-tag=[\"\']([^\"\']+)', ' '.join(row.get('mod_no', [])))),
    }
    if result['weight'] < 0 or not math.isfinite(result['weight']):
        raise ValueError('权重必须非负且有限；缺失或占位权重不能当真实概率')
    return result


def search_summary(rows, query, ilvl, limit):
    matches = [x for x in rows if query.casefold() in json.dumps(x, ensure_ascii=False).casefold()]
    available = [x for x in matches if x['level'] <= ilvl]
    available.sort(key=lambda x: x['level'], reverse=True)
    families = defaultdict(list)
    for row in matches:
        families[(row.get('section'), row['side'], tuple(sorted(row['groups'])))].append(row)
    return {'matching_count': len(available), 'shown_count': min(len(available), limit),
            'truncated': len(available) > limit, 'matches': available[:limit],
            'family_level_coverage': [
                {'section': section, 'side': side, 'groups': list(groups),
                 'recorded_levels': sorted({x['level'] for x in tiers}),
                 'available_levels': sorted({x['level'] for x in tiers if x['level'] <= ilvl})}
                for (section, side, groups), tiers in families.items()],
            'note': '记录等级覆盖来自本次效果匹配；完整阶级按家族核对。本物品可用的最高阶不等于全池T1；各来源不混算概率。'}


def pool_summary(rows, args, policy):
    rows = [normalize(x) for x in rows]
    available = [x for x in rows if x['level'] <= args.ilvl and
                 (not args.side or x['side'] == args.side) and
                 not set(x['groups']) & set(args.exclude_group)]
    groups = defaultdict(list)
    for row in available:
        groups[tuple(sorted(row['groups']))].append(row)
    kept, exceptions = [], []
    for key, tiers in groups.items():
        eligible = [x for x in tiers if x['level'] >= args.min_level]
        if not eligible and args.min_level:
            exceptions.append(list(key))
            eligible = tiers if policy == 'keep-all' else [x for x in tiers if x['level'] == max(t['level'] for t in tiers)]
        kept.extend(eligible)
    for row in kept:
        match = args.tag and args.tag.casefold() in [t.casefold() for t in row['tags']]
        row['adjusted_weight'] = row['weight'] * (args.multiplier if match else 1)
    total = sum(x['adjusted_weight'] for x in kept)
    targets = []
    for spec in args.target:
        family, separator, level = spec.partition('@')
        found = [x for x in kept if family in x['groups'] and (not separator or x['level'] == int(level))]
        share = sum(x['adjusted_weight'] for x in found) / total if total else None
        target = {'target': spec, 'weight': sum(x['adjusted_weight'] for x in found),
                  'weight_share_of_supplied_pool': share, 'mods': found}
        if args.side:
            target['probability_given_side_and_input_weights'] = share
        targets.append(target)
    search_rows = [x for x in rows if not args.side or x['side'] == args.side]
    search = search_summary(search_rows, args.find, args.ilvl, args.limit) if args.find else {'matches': [], 'matching_count': 0}
    return {'count': len(kept), 'total_weight': total, 'whole_type_exceptions': exceptions,
            'exception_policy': policy, 'targets': targets,
            'discovery': search,
            'eligible_matches': [x for x in kept if args.find and args.find.casefold() in json.dumps(x, ensure_ascii=False).casefold()][:args.limit],
            'probability_scope': '条件于新增该侧及输入权重正确' if args.side else '仅输入池权重占比；未提供实际选侧模型，不能当命中概率',
            'assumptions': '输入池已对应底材。最低等级类型例外按ModFamilyList组合近似分组，未确认等于客户端modifier type；品质倍率由调用者给定。'}


def deletion(item, side=None, lowest=False, add_side=None):
    mods = item['mods']
    if len({m['id'] for m in mods}) != len(mods) or any(m['side'] not in ('prefix', 'suffix') for m in mods):
        raise ValueError('词缀id必须唯一，side必须为prefix/suffix')
    candidates = [m for m in mods if not m.get('fractured', False) and m.get('removable', True)
                  and (not side or m['side'] == side)]
    if lowest and candidates:
        if any(not isinstance(m.get('mod_level'), int) or m['mod_level'] < 0 for m in candidates):
            raise ValueError('最低等级删除需要每条可删词的真实 mod_level；未知不当作0')
        level = min(m['mod_level'] for m in candidates)
        candidates = [m for m in candidates if m['mod_level'] == level]
    branches = []
    for m in candidates:
        counts = {s: sum(x['side'] == s for x in mods) - int(m['side'] == s) for s in ('prefix', 'suffix')}
        default_cap = 1 if item.get('rarity') == 'magic' else 3
        total_cap = item.get('caps', {}).get('total', 2 * default_cap)
        open_sides = [s for s, n in counts.items() if n < item.get('caps', {}).get(s, default_cap)
                      and sum(counts.values()) < total_cap]
        branches.append({'removed': m['id'], 'probability': 1 / len(candidates),
                         'loses_protected': bool(m.get('protected')), 'after_remove_counts': counts,
                         'possible_add_sides': open_sides, 'requested_add_side_fits': add_side in open_sides if add_side else None})
    return {'eligible_count': len(candidates), 'eligible': [m['id'] for m in candidates],
            'branches': branches,
            'empty_selector_scope': '无可删项时不由本工具判断通货是拒绝、仅新增还是无效果；该行为需具体机制说明' if not candidates else None,
            'assumption': '仅核算给定删除选择器；随机选择假设可删候选等权，未验证道具/预兆是否能联用。'}


def expectation(probability, roll, reset=0, initial=0, finish=0):
    values = (probability, roll, reset, initial, finish)
    if not all(math.isfinite(x) for x in values) or not 0 < probability <= 1 or min(values[1:]) < 0:
        raise ValueError('概率需在(0,1]，费用需为非负有限数')
    return initial + (roll + (1 - probability) * reset) / probability + finish


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    f = sub.add_parser('fetch', help='提取网页嵌入词缀JSON，只返回摘要；不打印网页全文')
    f.add_argument('--url', required=True); f.add_argument('--save', required=True)
    q = sub.add_parser('pool', help='汇总本地词缀池，目标格式为 family 或 family@level')
    q.add_argument('--file', required=True); q.add_argument('--section', help='查效果默认跨来源；算概率默认normal')
    q.add_argument('--ilvl', type=int, required=True); q.add_argument('--side', choices=['prefix', 'suffix'])
    q.add_argument('--min-level', type=int, default=0)
    q.add_argument('--exception-policy', choices=['unknown', 'keep-highest', 'keep-all'], default='unknown')
    q.add_argument('--exclude-group', action='append', default=[])
    q.add_argument('--target', action='append', default=[]); q.add_argument('--find')
    q.add_argument('--tag'); q.add_argument('--multiplier', type=float, default=1)
    q.add_argument('--limit', type=int, default=8)
    d = sub.add_parser('delete', help='给定item JSON的mods列表：id、side、fractured、protected、mod_level')
    d.add_argument('--file', required=True); d.add_argument('--side', choices=['prefix', 'suffix'])
    d.add_argument('--lowest-level', action='store_true'); d.add_argument('--add-side', choices=['prefix', 'suffix'])
    e = sub.add_parser('expect', help='只适用于失败能恢复同一状态的循环')
    e.add_argument('--probability', type=float, required=True); e.add_argument('--roll', type=float, required=True)
    e.add_argument('--reset', type=float, default=0); e.add_argument('--initial', type=float, default=0); e.add_argument('--finish', type=float, default=0)
    a = p.parse_args()
    try:
        if a.command == 'fetch':
            out = fetch_pool(a.url, a.save)
        elif a.command == 'pool':
            a.section = a.section or ('all' if a.find and not a.target else 'normal')
            if a.ilvl < a.min_level:
                raise ValueError('物品ilvl低于通货最低等级门槛，不能使用')
            if a.multiplier <= 0 or not math.isfinite(a.multiplier):
                raise ValueError('倍率必须为正有限数')
            data = read_data(a.file)
            if a.section == 'all':
                if not a.find or a.target:
                    raise ValueError('all仅用于--find跨来源查找，不可混合来源计算概率')
                found = []
                for section, rows in data.items():
                    if not isinstance(rows, list): continue
                    for raw in rows:
                        if not isinstance(raw, dict) or 'ModFamilyList' not in raw: continue
                        row = normalize(raw)
                        if not a.side or row['side'] == a.side:
                            found.append({'section': section, **row})
                out = search_summary(found, a.find, a.ilvl, a.limit)
            else:
                rows = data[a.section] if isinstance(data, dict) else data
                out = pool_summary(rows, a, 'keep-highest' if a.exception_policy == 'unknown' else a.exception_policy)
                if a.exception_policy == 'unknown' and out['whole_type_exceptions']:
                    out = {'status': 'conditional', 'note': '说明保证不排空整类；此处按ModFamilyList近似分组并采用公开资料支持的最高可用阶兜底。分组及具体兜底未经本次游戏实测，结果是条件计算。',
                           'scenarios': [out]}
        elif a.command == 'delete':
            out = deletion(read_data(a.file), a.side, a.lowest_level, a.add_side)
        else:
            out = {'expected_cost': expectation(a.probability, a.roll, a.reset, a.initial, a.finish),
                   'condition': '每次失败按reset费用回到同一状态、相同成功率；费用使用同一单位'}
        print(json.dumps(out, ensure_ascii=False))
    except (ValueError, KeyError, OSError) as exc:
        p.exit(2, json.dumps({'error': str(exc)}, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
