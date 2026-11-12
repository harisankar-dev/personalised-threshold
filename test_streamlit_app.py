import unittest
from streamlit.testing.v1 import AppTest

class StreamlitTests(unittest.TestCase):
 def test_initial_render(self):
  app=AppTest.from_file('streamlit_app.py').run(timeout=30)
  self.assertFalse(app.exception)
  self.assertEqual(len(app.tabs),3)
 def test_creative_and_simulation(self):
  app=AppTest.from_file('streamlit_app.py').run(timeout=30)
  next(w for w in app.text_area if w.label=='Ad copy').set_value('We know where you live.')
  next(w for w in app.button if w.label=='Analyze creative and campaign').click().run()
  self.assertFalse(app.exception)
  self.assertTrue(any(m.label=='Editorial screening score / 10' for m in app.metric))
  next(w for w in app.button if w.label=='Compare L0–L4').click().run()
  self.assertFalse(app.exception)
  self.assertEqual(len(app.session_state['simulation_result']['levels']),5)
  self.assertIsNone(app.session_state['simulation_result']['recommended_level'])
