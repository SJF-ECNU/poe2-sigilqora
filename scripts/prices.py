#!/usr/bin/env python3
"""PoE2 crafting material prices: isolated CN / international league markets.

Python >=3.10; stdlib only. Community APIs: poe.ninja and poecurrency.top.
Not an order book or a guaranteed executable quote.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import sys
import time
from urllib import parse, request, error

NINJA = 'https://poe.ninja/poe2/api/economy'
CN = 'https://poecurrency.top/api'
NINJA_TYPES = {'Currency','Fragments','Abyss','UncutGems','LineageSupportGems',
               'Essences','SoulCores','Idols','Runes','Ritual','Expedition',
               'Delirium','Breach','Verisium'}
CURRENCY_ALIASES = {
    'c':'c', 'chaos':'c','chaos orb':'c','混沌石':'c',
    'e':'e', 'ex':'e','exalted':'e','exalted orb':'e','崇高石':'e',
    'd':'d', 'div':'d','divine':'d','divine orb':'d','神圣石':'d',
}
CN_DISPLAY = {'c':'混沌石','e':'崇高石','d':'神圣石'}

class PriceError(Exception):
    pass


def _url(base, params=None):
    return base + ('?' + parse.urlencode(params) if params else '')


def _json_request(url, *, cache_dir, refresh=False, ttl=3600, timeout=10):
    cache_dir = pathlib.Path(cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()
    path = cache_dir / (key + '.json')
    if not refresh and path.is_file() and (time.time() - path.stat().st_mtime) < ttl:
        return json.loads(path.read_text(encoding='utf-8')), 'cache'
    ua = os.getenv('POE2_CRAFT_USER_AGENT', 'PoE2-Crafting-Skill/2.0 (personal read-only price lookup)')
    req = request.Request(url, headers={'Accept':'application/json','User-Agent':ua})
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(15_000_000)
    except (error.URLError, TimeoutError, OSError) as exc:
        raise PriceError(f'无法获取 {url}: {exc}。未自动跨服/跨赛季替代报价。') from exc
    try:
        obj = json.loads(raw.decode('utf-8-sig'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PriceError(f'{url} 返回了非 JSON 数据，不可作为价格') from exc
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding='utf-8')
    return obj, 'network'


def _from_provider(url, args):
    if args.fixture:
        return json.loads(pathlib.Path(args.fixture).read_text(encoding='utf-8')), 'fixture'
    return _json_request(url, cache_dir=args.cache_dir, refresh=args.refresh,
                         ttl=args.cache_ttl, timeout=args.timeout)


def _norm(s):
    return str(s or '').strip().casefold().replace(' ','').replace('_','').replace('-','')


def _valid_positive(x):
    if isinstance(x,bool): return None
    try:
        v=float(x)
        if not math.isfinite(v) or v<=0: return None
        return v
    except (ValueError,TypeError):
        return None


def _matches(text, needles):
    if not needles: return True
    t=_norm(text)
    return any(_norm(n)==t for n in needles)


def _get_leagues(args):
    if args.realm=='intl':
        url=NINJA+'/leagues'
        data, via=_from_provider(url,args)
        if not isinstance(data,list): raise PriceError('国际服 leagues 接口结构异常，停止报价')
        leagues=[{'id':x.get('id'),'name':x.get('name')} for x in data if isinstance(x,dict) and x.get('id')]
    else:
        url=_url(CN+'/season_list',{'version':'poe2'})
        data,via=_from_provider(url,args)
        if not isinstance(data,list): raise PriceError('国服 season_list 非赛季字符串数组，停止报价')
        leagues=[{'id':x,'name':x} for x in data if isinstance(x,str)]
    if not leagues: raise PriceError('赛季目录为空，停止报价')
    return leagues, url, via


def _select_league(args):
    if not args.league: raise PriceError('必须显式指定 --league <赛季ID|current>')
    if args.realm=='cn' and args.league=='current':
        # CN API explicitly says absence of 'season' means active league, not
        # an arbitrary translated global league id.
        return 'current'
    leagues,_,_=_get_leagues(args)
    if args.league=='current': return leagues[0]['id']
    matches=[x['id'] for x in leagues if args.league in (x['id'], x['name'])]
    if len(matches)!=1:
        raise PriceError(f'赛季 {args.league!r} 不在该服目录中；运行 leagues 查询有效赛季')
    return matches[0]


def _map_ninja_core_names(data):
    # The public spec calls it core.items; some observed snapshots put items
    # at the top level. Both carry item name metadata, never price themselves.
    core=data.get('core') or {}
    rows=core.get('items') or data.get('items') or []
    if isinstance(rows,dict): rows=list(rows.values())
    result={}
    if isinstance(rows,list):
        for x in rows:
            if isinstance(x,dict) and x.get('id'):
                result[str(x['id'])]=x.get('name') or x.get('id')
    return result


def parse_intl(data, *, category, names, unit=None):
    if not isinstance(data,dict) or not isinstance(data.get('lines'),list) or not isinstance(data.get('core'),dict):
        raise PriceError('poe.ninja 接口结构缺少 core / lines，不推测报价')
    core=data['core']
    primary=core.get('primary')
    if not isinstance(primary,(str,dict)) or not primary:
        raise PriceError('缺少 core.primary（计价通货），禁止假设是 C/D/E')
    primary_id=primary if isinstance(primary,str) else (primary.get('id') or primary.get('name'))
    if not primary_id: raise PriceError('core.primary 无可识别名称')
    labels=_map_ninja_core_names(data)
    lines=data['lines']
    base_lines={str(x.get('id')): _valid_positive(x.get('primaryValue')) for x in lines if isinstance(x,dict)}
    wanted_unit=unit or str(primary_id)
    unit_key=_norm(wanted_unit)
    primary_key=_norm(primary_id)
    if unit_key==primary_key or _norm(labels.get(str(primary_id),''))==unit_key:
        factor=1.0
    else:
        # Relative to another *observed* traded currency line in same snapshot.
        target_id=next((k for k,v in labels.items() if _norm(k)==unit_key or _norm(v)==unit_key),None)
        if target_id is None: target_id=next((k for k in base_lines if _norm(k)==unit_key),None)
        target_price=base_lines.get(target_id)
        if target_price is None: raise PriceError(f'快照没有 {wanted_unit} 对 {primary_id} 的有效报价；不能自动换算')
        factor=1/target_price
    results=[]
    for line in lines:
        if not isinstance(line,dict): continue
        item_id=str(line.get('id',''))
        name=labels.get(item_id,item_id)
        if not (_matches(name,names) or (names and _matches(item_id,names))):continue
        price=_valid_positive(line.get('primaryValue'))
        if price is None:continue
        results.append({'name':name,'id':item_id,'category':category,
                        'price':round(price*factor,10),'unit':wanted_unit,
                        'native_price':price,'native_unit':primary_id,
                        'volume_primary':line.get('volumePrimaryValue'),
                        'side':'exchange_overview','error':False,
                        'timestamp':core.get('timestamp')})
    if names and not results: raise PriceError('指定材料在该赛季/分类中找不到有效报价（不跨服补价）')
    return results


def _cn_rows(data):
    # Official CN documentation (poecurrency.top/api.html): JSON array of
    # groups with items; each row has currency_unit and latest_sell1/buy1.
    if not isinstance(data,list): raise PriceError('国服 summary 非分组 JSON 数组，停止报价')
    out=[]
    for group in data:
        if not isinstance(group,dict) or not isinstance(group.get('items'),list):
            raise PriceError('国服 summary 分组缺少 items[]，停止报价')
        for item in group['items']:
            if not isinstance(item,dict): continue
            r={**item}
            r.setdefault('category_label',group.get('category_label'))
            out.append(r)
    return out


def _cn_unit(x):
    # Never infer e/c/d from PoE2 defaults: items may be quoted in d.
    return CURRENCY_ALIASES.get(str(x or '').strip().casefold())


def parse_cn(data, *, names, category=None, side='sell', unit=None,
             rate_e_per_d=None, rate_c_per_e=None):
    rows=_cn_rows(data)
    if side not in ('sell','buy'): raise PriceError('side 只能为 buy 或 sell')
    result=[]
    for r in rows:
        n=str(r.get('item_name') or '')
        english=str(r.get('engname') or '')
        if not (_matches(n,names) or (names and _matches(english,names))):continue
        if category and category!=str(r.get('category_label') or ''):continue
        raw_unit=_cn_unit(r.get('currency_unit'))
        if raw_unit is None:
            # Fail closed for mismatched / missing unit. Do not assume e.
            continue
        raw_price=_valid_positive(r.get('latest_sell1' if side=='sell' else 'latest_buy1'))
        used_field='latest_'+side+'1'
        if raw_price is None:
            raw_price=_valid_positive(r.get(side+'_avg'))
            used_field=side+'_avg'
        if raw_price is None:continue
        error_flag=bool(r.get('error'))
        price=raw_price
        out_unit=unit or raw_unit
        if out_unit not in ('c','e','d'):
            raise PriceError('国服只支持单位 c/e/d；不要用国际服英文通货 ID')
        if out_unit != raw_unit:
            if out_unit == 'e' and raw_unit=='d' and rate_e_per_d: price=raw_price*rate_e_per_d
            elif out_unit == 'e' and raw_unit=='c' and rate_c_per_e: price=raw_price/rate_c_per_e
            elif out_unit == 'c' and raw_unit=='e' and rate_c_per_e: price=raw_price*rate_c_per_e
            elif out_unit == 'c' and raw_unit=='d' and rate_e_per_d and rate_c_per_e: price=raw_price*rate_e_per_d*rate_c_per_e
            elif out_unit == 'd' and raw_unit=='e' and rate_e_per_d: price=raw_price/rate_e_per_d
            elif out_unit == 'd' and raw_unit=='c' and rate_e_per_d and rate_c_per_e: price=raw_price/rate_c_per_e/rate_e_per_d
            else: raise PriceError(f'{n}: {raw_unit}->{out_unit} 缺少同服同赛季汇率，需补 --e-per-d/--c-per-e')
        result.append({'name':n,'english':english,'category':r.get('category_label'),
                       'price':round(price,10),'unit':out_unit,
                       'native_price':raw_price,'native_unit':raw_unit,
                       'side':side,'source_field':used_field,'error':error_flag,
                       'error_info':r.get('error_info'),
                       'timestamp':r.get('latest_datetime')})
    if names and not result: raise PriceError('未找到国服目标材料的有效报价，或接口缺少可识别字段')
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description='PoE2 材料行情：国际服 poe.ninja / 国服 poecurrency.top；严格隔离赛季')
    parser.add_argument('command',choices=['leagues','quote','snapshot'])
    parser.add_argument('--realm',choices=['intl','cn'],required=True,help='国际服 intl / 国服 cn')
    parser.add_argument('--league',help='API 赛季 ID（或者 current）；quote/snapshot 必须指定')
    parser.add_argument('--category',help='国际服类型 Currency/Essences/Ritual/...；国服 category_label 可选')
    parser.add_argument('--item',action='append',help='材料名称或 ID；可重复 --item')
    parser.add_argument('--unit',help='国际服参照通货 ID / 国服 c、e、d；不指定保持原始计价单位')
    parser.add_argument('--side',choices=['sell','buy'],default='sell',help='国服默认参考卖1（买入参考价），可改买1')
    parser.add_argument('--e-per-d',type=float,help='手动传入同服同赛季 1D=多少E 的现价')
    parser.add_argument('--c-per-e',type=float,help='手动传入同服同赛季 1E=多少C 的现价')
    parser.add_argument('--fixture',help='离线测试用 JSON；从该文件读取，绝不访问网络')
    parser.add_argument('--cache-dir',default='.pcache/poe2-prices',help='默认写当前工作区 .pcache/poe2-prices')
    parser.add_argument('--cache-ttl',type=int,default=3600,help='缓存秒数，默认 3600')
    parser.add_argument('--refresh',action='store_true',help='刷新缓存；请勿频繁请求')
    parser.add_argument('--timeout',type=float,default=10)
    args=parser.parse_args(argv)
    try:
        if args.command=='leagues':
            leagues,url,via=_get_leagues(args)
            result={'realm':args.realm,'source':url,'transport':via,'leagues':leagues}
        else:
            league=_select_league(args) if not args.fixture else (args.league or 'offline-fixture')
            # The Chinese market uses an omitted `season` query parameter for its
            # current league. Resolve the displayed league ID independently so
            # downstream cost sheets can trace the exact same realm and season.
            resolved_league=league
            if args.realm=='cn' and league=='current' and not args.fixture:
                latest,_,_=_get_leagues(args)
                resolved_league=latest[0]['id']
            if args.realm=='intl':
                category=args.category or 'Currency'
                if category not in NINJA_TYPES: raise PriceError(f'不支持的国际服 category: {category}')
                url=_url(NINJA+'/exchange/current/overview',{'league':league,'type':category})
            else:
                url=_url(CN+'/summary',{'version':'2',**({} if league=='current' else {'season':league})})
            data,via=_from_provider(url,args)
            if args.command=='snapshot':
                # For debugging schema; does not guess normalized pricing.
                result={'realm':args.realm,'league':resolved_league,'requested_league':args.league,'source':url,'transport':via,'data':data}
            else:
                if not args.item: raise PriceError('quote 必须指定至少一个 --item')
                for field in (args.e_per_d,args.c_per_e):
                    if field is not None and (_valid_positive(field) is None):raise PriceError('汇率必须是正数')
                if args.realm=='intl':
                    rows=parse_intl(data,category=category,names=args.item,unit=args.unit)
                else:
                    rows=parse_cn(data,names=args.item,category=args.category,side=args.side,
                                  unit=args.unit,rate_e_per_d=args.e_per_d,rate_c_per_e=args.c_per_e)
                missing=[x for x in args.item if not any(_matches(r.get('name'),[x]) or _matches(r.get('english'),[x]) or _matches(r.get('id'),[x]) for r in rows)]
                unusable=[r for r in rows if r['error']]
                usable=[r for r in rows if not r['error']]
                result={'realm':args.realm,'league':resolved_league,'requested_league':args.league,'source':url,'transport':via,
                        'price_type':'market_reference_not_guaranteed_trade',
                        'fetched_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                        'quotes':usable,'missing':missing,'unusable':unusable,
                        'complete':not (missing or unusable)}
                if missing or unusable:
                    result['cost_scope']='仅quotes为有效行情；缺项或异常费用仍未知，不能计算完整成本或将其当0'
                    print(json.dumps(result,ensure_ascii=False,indent=2))
                    print(json.dumps({'ok':False,'error':'缺价或存在OCR/陈旧异常；已保留有效报价，完整费用未知'},ensure_ascii=False),file=sys.stderr)
                    return 2
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (PriceError,ValueError) as exc:
        print(json.dumps({'ok':False,'error':str(exc),'realm':args.realm,
                          'league':args.league},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
