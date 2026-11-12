import io,json,os,unittest
from unittest.mock import patch
from api.index import handler
class VercelRoutes(unittest.TestCase):
 def request(self,method,route,payload=None):
  h=handler.__new__(handler);h.path='/api/index?route='+route
  raw=json.dumps(payload).encode() if payload is not None else b''
  h.headers={'Content-Length':str(len(raw)),'Content-Type':'application/json'};h.rfile=io.BytesIO(raw);out={}
  h.send_bytes=lambda status,data,mime:out.update(status=status,data=json.loads(data))
  getattr(h,'do_'+method)();return out
 def test_research(self):self.assertEqual(self.request('GET','research')['data']['threshold']['status'],'insufficient_evidence')
 def test_config(self):
  with patch.dict(os.environ,{'VERCEL':'1'}):self.assertTrue(self.request('GET','config')['data']['hosted_ocr'])
 def test_analyze(self):
  r=self.request('POST','analyze',{'text':'We know where you live.'});self.assertEqual(r['status'],200);self.assertGreater(r['data']['privacy_score'],0)
 def test_simulation(self):self.assertIn('segments',self.request('GET','simulation')['data'])
