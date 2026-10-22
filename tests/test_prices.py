import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('prices',ROOT/'scripts/prices.py')
p=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)
FIX=Path(__file__).resolve().parent/'fixtures'

class TestPrices(unittest.TestCase):
    def test_intl(self):
        data=json.loads((FIX/'intl.json').read_text())
        x=p.parse_intl(data,category='Currency',names=['Perfect Exalted Orb'],unit='Chaos Orb')
        self.assertAlmostEqual(x[0]['price'],16.0)
        self.assertEqual(x[0]['native_unit'],'divine')
    def test_intl_fail_unit(self):
        data=json.loads((FIX/'intl.json').read_text())
        with self.assertRaises(p.PriceError):
            p.parse_intl(data,category='Currency',names=['Perfect Exalted Orb'],unit='exalted')
    def test_cn_sell(self):
        data=json.loads((FIX/'cn.json').read_text())
        x=p.parse_cn(data,names=['完美崇高石'],side='sell')
        self.assertEqual((x[0]['price'],x[0]['unit']),(15,'e'))
    def test_cn_rate(self):
        data=json.loads((FIX/'cn.json').read_text())
        x=p.parse_cn(data,names=['完美崇高石'],unit='c',rate_c_per_e=10)
        self.assertEqual(x[0]['price'],150)
    def test_cn_no_cross_unit_implicit(self):
        data=json.loads((FIX/'cn.json').read_text())
        with self.assertRaises(p.PriceError):p.parse_cn(data,names=['左旋崇高预兆'],unit='e')
    def test_cli_no_market_mix(self):
        cmd=[sys.executable,str(ROOT/'scripts/prices.py'),'quote','--realm','cn','--league','current','--item','左旋崇高预兆','--fixture',str(FIX/'cn.json')]
        result=subprocess.run(cmd,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('OCR',result.stderr)
    def test_cli_intl(self):
        cmd=[sys.executable,str(ROOT/'scripts/prices.py'),'quote','--realm','intl','--league','Standard','--category','Currency','--item','Perfect Exalted Orb','--unit','Chaos Orb','--fixture',str(FIX/'intl.json')]
        result=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        obj=json.loads(result.stdout)
        self.assertEqual(obj['realm'],'intl')
        self.assertEqual(obj['quotes'][0]['price'],16)
    def test_fail_unknown_cn_schema(self):
        with self.assertRaises(p.PriceError):p.parse_cn({'arbitrary':123},names=['Any'])
    def test_cn_current_displays_exact_league_and_omits_query_parameter(self):
        data=json.loads((FIX/'cn.json').read_text())
        calls=[]
        def provider(url,args):
            calls.append(url)
            return data,'test-network'
        with patch.object(p,'_get_leagues',return_value=([{'id':'FakeCNSeason','name':'FakeCNSeason'}],'source','test-network')):
            with patch.object(p,'_from_provider',side_effect=provider):
                out=StringIO()
                with redirect_stdout(out):
                    code=p.main(['quote','--realm','cn','--league','current','--item','完美崇高石'])
        self.assertEqual(code,0)
        result=json.loads(out.getvalue())
        self.assertEqual(result['league'],'FakeCNSeason')
        self.assertEqual(result['requested_league'],'current')
        self.assertIn('/api/summary?version=2',calls[0])
        self.assertNotIn('season=',calls[0])
    def test_cn_explicit_historical_season_is_sent(self):
        data=json.loads((FIX/'cn.json').read_text())
        calls=[]
        def provider(url,args):
            calls.append(url)
            return data,'test-network'
        with patch.object(p,'_get_leagues',return_value=([{'id':'ArchiveA','name':'ArchiveA'}],'source','test-network')):
            with patch.object(p,'_from_provider',side_effect=provider):
                out=StringIO()
                with redirect_stdout(out):
                    code=p.main(['quote','--realm','cn','--league','ArchiveA','--item','完美崇高石'])
        self.assertEqual(code,0)
        self.assertIn('season=ArchiveA',calls[0])

if __name__=='__main__':unittest.main()
