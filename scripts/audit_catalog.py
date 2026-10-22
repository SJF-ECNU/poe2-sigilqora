#!/usr/bin/env python3
"""Offline static coverage/integrity checker for the PoE2 crafting skill.

No network calls and no verification of current league mechanics. Use poe2db for current rules.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'references'
BASE_REQUIRED = {
    'SKILL.md', 'README.md',
    'references/mechanism-checklist.md',
    'references/crafting-items.md',
    'references/catalog-index.md',
    'references/advanced-interactions.md',
    'references/crafting-logic.md',
    'references/state-and-planning.md',
    'references/data-sources.md',
    'references/compatibility-and-evidence.md',
    'references/known-conflicts.json',
    'scripts/prices.py', 'scripts/lookup_item.py', 'scripts/build_item_contracts.py',
    'references/critical-rules.md', 'references/material-audit.md', 'references/item-contracts.json',
    'references/item-descriptions.json',
}

def check():
    errors=[]
    for f in sorted(BASE_REQUIRED):
        if not (ROOT/f).is_file():errors.append(f'missing {f}')
    if errors:return errors
    d=json.loads((REF/'catalog-audit.json').read_text(encoding='utf-8'))
    catalog=(REF/'catalog-index.md').read_text(encoding='utf-8')
    skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
    summary=(REF/'crafting-items.md').read_text(encoding='utf-8')
    advanced=(REF/'advanced-interactions.md').read_text(encoding='utf-8')
    checklist=(REF/'mechanism-checklist.md').read_text(encoding='utf-8')
    fam=d['essence_base_families']; spec=d['essence_special']; alloys=d['alloys']; omens=[n for v in d['omens'].values() for n in v]; runes=d['runes']
    counts={'essence_and_alloy':len(fam)*4+len(spec)+len(alloys),'omen_and_saga':len(omens),'basic_rune':len(runes), 'currency_tab':len(d['currency_tab']),
            'fate_of_vaal':len(d['fate_of_vaal']), 'abyss_bones':len(d['abyss_bones'])}
    for k,v in d['expected'].items():
        if counts[k]!=v:errors.append(f'{k} count expected {v}, actual {counts[k]}')
    if len(set(omens))!=len(omens):errors.append('duplicate omens')
    if len(set(runes))!=len(runes):errors.append('duplicate runes')
    if len(set(alloys))!=len(alloys):errors.append('duplicate alloys')
    for f in fam:
        for grade in ('Lesser ', '', 'Greater ', 'Perfect '):
            name=f'{grade}Essence of {f}'
            if name not in catalog:errors.append(f'catalog missing: {name}')
    for n in spec+alloys+omens+runes+d['currency_tab']+d['fate_of_vaal']+d['abyss_bones']:
        if n not in catalog:errors.append(f'catalog missing: {n}')
    for n in ('Astrid\'s Creativity','Serle\'s Triumph','Thrud\'s Might',
              'Cadigan\'s Epiphany','Essence of the Breach','Omen of Whittling',
              'Fracturing Orb','Vaal Siphoner','Ancient Potent Liquid Contempt',
              'Socket-bound','Orb of Extraction'):
        if n not in catalog+summary+advanced:errors.append(f'key mechanism missing: {n}')
    ids=re.findall(r'\|\s*(M\d\d)\s*\|',checklist)
    if ids!=[f'M{i:02d}' for i in range(1,29)]:errors.append('28 mechanism IDs not sequential / distinct')
    if not all(x in skill for x in ('mechanism-checklist.md','compatibility-and-evidence.md','known-conflicts.json','catalog-index.md','advanced-interactions.md')):
        errors.append('skill missing knowledge or mechanism reference links')
    # Important: name coverage is weaker than operation safety; enforce per-item
    # contract presence and irreversible-action sentinel data as an offline gate.
    contracts=json.loads((REF/'item-contracts.json').read_text(encoding='utf-8'))['items']
    mapping={o['name']:o for o in contracts}
    descriptions=json.loads((REF/'item-descriptions.json').read_text(encoding='utf-8'))['items']
    for name, record in mapping.items():
        source=descriptions.get(name)
        if source and record.get('description') != source['description']:
            errors.append(f'generated description differs from extracted source: {name}')
        if not source and record.get('effect_coverage') != 'category_only':
            errors.append(f'missing source must remain category_only: {name}')
    if len(mapping)!=329:errors.append(f'item contract expected 329 distinct names, actual {len(mapping)}')
    names=[f'{grade}Essence of {f}' for f in fam for grade in ('Lesser ','','Greater ','Perfect ')]
    names+=spec+alloys+omens+runes+d['currency_tab']+d['fate_of_vaal']+d['abyss_bones']
    if len(set(names))!=274:errors.append('original catalog does not have 274 unique baseline items')
    for n in names:
        if n not in mapping: errors.append(f'missing operation contract: {n}')
    req=('target','preconditions','state_effects','conflict_and_capacity','fail_and_irreversibility','source_url','verification_level','live_required')
    for n,record in mapping.items():
        for k in req:
            if not record.get(k):errors.append(f'incomplete item contract: {n}/{k}')
    for n in ('Vaal Blacksmith\'s Infuser','Vaal Armourer\'s Infuser','Vaal Catalysing Infuser','Vaal Arcanist\'s Infuser'):
        obj=mapping.get(n,{}); check=str(obj.get('preconditions',''))+str(obj.get('state_effects',''))+str(obj.get('fail_and_irreversibility',''))
        for term in ('20%','+10%','腐化'):
            if term not in check:errors.append(f'infuser missing {term}: {n}')
    if '销毁整件装备' not in mapping.get('Orb of Extraction',{}).get('state_effects',''):errors.append('extraction destruction risk missing')
    for n in ("Yaomac's Orb of Sacrifice","Kopec's Orb of Sacrifice","Kamasa's Orb of Sacrifice","Yugul's Orb of Sacrifice"):
        if '随机移除' not in mapping.get(n,{}).get('state_effects',''):errors.append(f'sacrifice deletion risk missing: {n}')
    critical=(REF/'critical-rules.md').read_text(encoding='utf-8')
    if 'Minimum Modifier Level' not in critical or 'item level' not in critical or 'R22' not in critical:
        errors.append('missing complete critical rules')
    return errors

if __name__=='__main__':
    errs=check()
    if errs:
        for err in errs: print('ERROR:',err)
        sys.exit(1)
    print('PASS: baseline = 95 Essence/Alloy, 50 Omen/Saga, 64 basic Runes, 37 Currency, 16 Vaal, 12 Abyss Bone')
    print('PASS: 28 mechanism categories, 22 critical rules, 329 operation contracts and irreversible-risk sentinels present')
    print('NOTE: static audit is not a live PoE2 rules check, modifier-weight check, or trading API test')
