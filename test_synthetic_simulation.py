import unittest,json,csv
from pathlib import Path
from synthetic_simulation import evaluate,MODEL
from threshold_engine import current_dataset_status
class SimulationTests(unittest.TestCase):
 def payload(self):return dict(profile=[4,4,4,4],threshold=7,minimum_relevance=1,permissions=dict(context='yes',behavior='yes',history='yes'),costs=[0,10,20,30,40],headroom=100)
 def test_all_levels(self):
  r=evaluate(self.payload());self.assertEqual([x['level'] for x in r['levels']],['L0','L1','L2','L3','L4']);self.assertEqual(r['recommended_level'],'L0')
 def test_unknown_hold(self):
  p=self.payload();p['permissions']={};self.assertFalse(evaluate(p)['levels'][4]['eligible'])
 def test_behavior(self):
  p=self.payload();p['permissions']['behavior']='no';r=evaluate(p);self.assertFalse(r['levels'][2]['eligible']);self.assertFalse(r['levels'][4]['eligible']);self.assertTrue(r['levels'][3]['eligible'])
 def test_history(self):
  p=self.payload();p['permissions']['history']='no';self.assertFalse(evaluate(p)['levels'][3]['eligible'])
 def test_budget(self):
  p=self.payload();p['headroom']=5;self.assertFalse(evaluate(p)['levels'][1]['eligible'])
 def test_missing_cost(self):
  p=self.payload();p['costs']=[None]*5;self.assertIsNone(evaluate(p)['recommended_level'])
 def test_missing_input(self):
  with self.assertRaises(ValueError):evaluate({})
 def test_nonfinite(self):
  p=self.payload();p['profile'][0]=float('nan')
  with self.assertRaises(ValueError):evaluate(p)
 def test_segments(self):
  self.assertEqual(sum(s['consumers'] for s in MODEL['segments']),300)
  p=self.payload();p['segment']=MODEL['segments'][0]['name'];self.assertEqual(len(evaluate(p)['levels']),5)
 def test_split_and_source(self):
  rows=list(csv.DictReader(Path('synthetic_demo/exposures.csv').read_text().splitlines()));a={r['synthetic_consumer_id'] for r in rows if r['split']=='train'};b={r['synthetic_consumer_id'] for r in rows if r['split']=='test'};self.assertFalse(a&b);self.assertTrue(all(r['dataset_type'].startswith('SYNTHETIC') for r in rows))
 def test_ranges_and_determinism(self):
  a=evaluate(self.payload());self.assertEqual(a,evaluate(self.payload()));self.assertTrue(all(1<=r['discomfort']<=7 and 1<=r['relevance']<=7 for r in a['levels']))
 def test_empirical_abstention(self):self.assertEqual(current_dataset_status()['status'],'insufficient_evidence')
