"""Operation/data arithmetic checks; no Agent or game-behavior acceptance."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lookup_item import load_contracts, search, compact, relations
from craft_math import pool_summary, deletion
spec=importlib.util.spec_from_file_location('audit_prices',ROOT/'scripts/prices.py')
prices=importlib.util.module_from_spec(spec);spec.loader.exec_module(prices)

class FoundationsAudit(unittest.TestCase):
    def test_sanctification_terminal_effect_is_exposed_by_lookup(self):
        result=search(load_contracts(),name='Omen of Sanctification')
        self.assertEqual(len(result),1)
        record=compact(result[0])
        self.assertEqual(record['modifies']['requires'],'rare_and_not_sanctified')
        self.assertIs(record['modifies']['result_modifiable'],False)
        self.assertIs(record['modifies']['repeatable_on_same_item'],False)
        self.assertEqual(record['relation_evidence']['sanctified_state']['status'],
                         'confirmed_in_user_context')
        self.assertEqual(result[0]['description'],[
            'While this item is active in your inventory your next Divine Orb used on a Rare item will Sanctify it'])

    def test_queries_preserve_different_effects_and_unknown_conditions(self):
        items=load_contracts()
        fire={x['name'] for x in search(items,query='品质 火')}
        caster={x['name'] for x in search(items,query='品质 施法')}
        self.assertTrue(fire and caster)
        self.assertFalse(fire & caster)
        self.assertEqual(search(items,query='品质 不存在的限定条件'),[])
        jewels=search(items,query='珠宝 品质')
        self.assertTrue(jewels)
        self.assertTrue(all(x['name'].startswith('Refined ') for x in jewels))

    def test_per_target_effects_and_trigger_stages(self):
        items=load_contracts();data={x['name']:x for x in items}
        flame=compact(data['Greater Essence of Flames'])
        self.assertTrue(flame['target_effects'])
        self.assertEqual(flame['effect_coverage'],'source_description')
        self.assertTrue(all('Weapon' in x['target'] or 'Bow' in x['target'] or 'Crossbow' in x['target'] for x in flame['target_effects']))
        for name in ('Essence of Hysteria','Essence of Horror','Essence of Insanity','Essence of Delirium','Essence of the Abyss','Essence of the Breach'):
            mods=relations(data[name],items)['modifiers']
            self.assertEqual({x['modifies']['delete_side'] for x in mods},{'prefix','suffix'})
        bone={x['name'] for x in relations(data['Preserved Collarbone'],items)['modifiers']}
        self.assertIn('Omen of the Sovereign',bone)
        self.assertIn('Omen of Abyssal Echoes',bone)
        self.assertIn('Omen of Greater Exaltation',{x['name'] for x in relations(data['Exalted Orb'],items)['modifiers']})

    def test_discovery_and_probability_filters_are_distinct(self):
        rows=[{'name':'a','level':10,'side':'prefix','groups':['A'],'weight':10},
              {'name':'a','level':60,'side':'prefix','groups':['A'],'weight':10},
              {'name':'b','level':80,'side':'prefix','groups':['B'],'weight':10},
              {'name':'c','level':60,'side':'suffix','groups':['C'],'weight':10}]
        a=argparse.Namespace(ilvl=70,side='prefix',exclude_group=['A'],min_level=50,
                             tag=None,multiplier=1,target=['A@60'],find='a',limit=8)
        out=pool_summary(rows,a,'keep-highest')
        self.assertEqual(out['eligible_matches'],[])
        self.assertEqual(out['discovery']['matching_count'],2)
        self.assertEqual(out['targets'][0]['weight'],0)
        a.side=None;a.exclude_group=[];a.find=None
        out=pool_summary(rows,a,'keep-highest')
        self.assertNotIn('probability_given_side_and_input_weights',out['targets'][0])
        self.assertEqual(out['targets'][0]['weight_share_of_supplied_pool'],.5)

    def test_total_capacity_and_empty_delete_scope(self):
        item={'rarity':'rare','caps':{'prefix':5,'suffix':5,'total':4},
              'mods':[{'id':str(i),'side':'prefix' if i<3 else 'suffix'} for i in range(5)]}
        self.assertTrue(all(not x['possible_add_sides'] for x in deletion(item)['branches']))
        item={'mods':[{'id':'locked','side':'prefix','fractured':True}]}
        self.assertEqual(deletion(item)['eligible_count'],0)
        self.assertIsNotNone(deletion(item)['empty_selector_scope'])

    def test_partial_quote_preserves_valid_rows_and_rejects_total(self):
        fixture=ROOT/'tests/fixtures/cn.json'
        valid=prices.parse_cn(json.loads(fixture.read_text()),names=None)
        good=next(x for x in valid if not x['error'])
        output=io.StringIO();errors=io.StringIO()
        with patch.object(prices,'parse_cn',return_value=[good]), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code=prices.main(['quote','--realm','cn','--fixture',str(fixture),'--item',good['name'],'--item','missing'])
        result=json.loads(output.getvalue())
        self.assertEqual(code,2)
        self.assertFalse(result['complete'])
        self.assertEqual(result['quotes'],[good])
        self.assertEqual(result['missing'],['missing'])

if __name__=='__main__':unittest.main()
