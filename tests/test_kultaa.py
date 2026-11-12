"""Auditable native-dynamics regression tests; evaluate generated spike ticks."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from kultaa import truth,logic,learn,schedules

class GNLogic(unittest.TestCase):
    def test_xor(self):
        self.assertEqual(truth([-4.5,-4.5]),{"00":[],"10":[8],"01":[8],"11":[]})
    def test_and(self):
        self.assertEqual(truth([-2.5,-2.5]),{"00":[],"10":[],"01":[],"11":[8]})
    def test_innovation(self):
        self.assertEqual(truth([-5,5]),{"00":[],"10":[8],"01":[],"11":[]})
    def test_omission(self):
        self.assertEqual(truth([5,-5]),{"00":[],"10":[],"01":[8],"11":[]})
    def test_one_tick_breaks_xor(self):
        self.assertTrue(logic([1,1],[-4.5,-4.5],[0,1])[-1])

class GNMemory(unittest.TestCase):
    def test_empty_learns(self):
        d=learn(schedules()["empty_single"])
        self.assertEqual(d["innovation"],[8])
        self.assertEqual(d["omission"],[])
        self.assertEqual(d["prediction"][:4],[36,68,100,132])
    def test_two_slot_learning(self):
        d=learn(schedules()["empty_two"])
        self.assertEqual(d["innovation"],[8,24])
        self.assertEqual(d["prediction"][:4],[36,52,68,84])
    def test_stop(self):
        d=learn(schedules()["stop_after_5"])
        self.assertEqual(d["omission"],[168])
        self.assertEqual(d["prediction"][-1],164)
    def test_transient_omission(self):
        d=learn(schedules()["omit_at_5"])
        self.assertEqual(d["omission"],[168])
        self.assertEqual(d["innovation"],[8,200])
        self.assertNotIn(196,d["prediction"])
        self.assertIn(228,d["prediction"])
    def test_transient_extra(self):
        d=learn(schedules()["extra_at_5"])
        self.assertEqual(d["innovation"],[8,184])
        self.assertEqual(d["omission"],[216])
        self.assertIn(212,d["prediction"])
        self.assertNotIn(244,d["prediction"])
    def test_add_second(self):
        d=learn(schedules()["add_second_at_5"])
        self.assertIn(184,d["innovation"])
        self.assertIn(212,d["prediction"])
        self.assertIn(404,d["prediction"])
    def test_no_feedback(self):
        d=learn(schedules()["empty_single"],write=False,erase=False)
        self.assertEqual(d["prediction"],[])
        self.assertGreater(len(d["innovation"]),10)
    def test_no_erase(self):
        d=learn(schedules()["stop_after_5"],erase=False)
        self.assertGreater(len(d["omission"]),5)

if __name__=="__main__":
    unittest.main()
