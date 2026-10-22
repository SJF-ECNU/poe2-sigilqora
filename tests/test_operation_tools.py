"""Arithmetic and operation applicability; not a substitute for DSH evaluation."""
import argparse
import io
import json
import tempfile
from unittest.mock import patch
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from craft_math import fetch_pool, deletion, expectation, pool_summary
from lookup_item import load_contracts, relations, search


class OperationTools(unittest.TestCase):
    def test_base_page_uses_its_declared_class_link(self):
        pages = [io.BytesIO(b'<a class="ItemClasses " href="TestClass">TestClass</a>'),
                 io.BytesIO(b'new ModsView({"normal": []})')]
        with tempfile.TemporaryDirectory() as tmp, patch('craft_math.urlopen', side_effect=pages) as call:
            out = fetch_pool('https://example.org/us/TestBase', str(Path(tmp) / 'pool.json'))
            self.assertEqual(out['source'], 'https://example.org/us/TestClass')
            self.assertEqual(out['base_page'], 'https://example.org/us/TestBase')
            self.assertEqual(call.call_count, 2)

    def test_effect_search_does_not_match_opposite_side_warning(self):
        found = search(load_contracts(), query='精华 删除 后缀')
        names = {r['name'] for r in found}
        self.assertIn('Omen of Dextral Crystallisation', names)
        self.assertNotIn('Omen of Sinistral Crystallisation', names)

    def test_related_operations_use_actual_trigger_family(self):
        items = load_contracts()
        for name in ('Essence of the Breach', 'Swift Alloy'):
            mods = relations(next(r for r in items if r['name'] == name), items)['modifiers']
            self.assertEqual({r['modifies']['delete_side'] for r in mods}, {'prefix', 'suffix'})
        regular = next(r for r in items if r['name'] == 'Exalted Orb')
        self.assertNotIn('Omen of Dextral Crystallisation', {r['name'] for r in relations(regular, items)['modifiers']})

    def test_fracture_changes_denominator_and_delete_then_add_slots(self):
        item = {'mods': [{'id': 'locked', 'side': 'prefix', 'fractured': True},
                         {'id': 'good', 'side': 'prefix', 'protected': True},
                         {'id': 'p', 'side': 'prefix'}, {'id': 's1', 'side': 'suffix'}, {'id': 's2', 'side': 'suffix'}]}
        out = deletion(item)
        self.assertEqual(out['eligible_count'], 4)
        self.assertTrue(all(b['probability'] == .25 for b in out['branches']))
        suffix = deletion(item, side='suffix', add_side='prefix')
        self.assertTrue(all(not b['loses_protected'] for b in suffix['branches']))
        self.assertTrue(all(not b['requested_add_side_fits'] for b in suffix['branches']))

    def test_unknown_level_and_tied_lowest(self):
        item = {'mods': [{'id': 'a', 'side': 'prefix'}, {'id': 'b', 'side': 'suffix', 'mod_level': 1}]}
        with self.assertRaises(ValueError): deletion(item, lowest=True)
        item['mods'][0]['mod_level'] = 1
        self.assertEqual(deletion(item, lowest=True)['eligible_count'], 2)

    def test_price_reversal_and_whole_type_exception(self):
        self.assertEqual(expectation(.02, 1), 50)
        self.assertEqual(expectation(.1, 6, 2), 78)
        self.assertAlmostEqual(expectation(.1, 3, 2), 48)
        rows = [{'name': 'low', 'level': 10, 'side': 'prefix', 'groups': ['A'], 'weight': 10},
                {'name': 'high', 'level': 40, 'side': 'prefix', 'groups': ['A'], 'weight': 5},
                {'name': 'other', 'level': 60, 'side': 'prefix', 'groups': ['B'], 'weight': 15}]
        args = argparse.Namespace(ilvl=75, side='prefix', exclude_group=[], min_level=50,
                                  tag=None, multiplier=1, target=['A@40'], find=None, limit=8)
        highest = pool_summary(rows, args, 'keep-highest')
        all_tiers = pool_summary(rows, args, 'keep-all')
        self.assertEqual(highest['targets'][0]['probability_given_side_and_input_weights'], .25)
        self.assertAlmostEqual(all_tiers['targets'][0]['probability_given_side_and_input_weights'], 1 / 6)


if __name__ == '__main__':
    unittest.main()
