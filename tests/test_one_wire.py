"""Independent regression tests of Opus one-wire architecture and control."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from one_wire import run,world_beats,late_success,compare_switch,compare_nine_ring

class OneWire(unittest.TestCase):
    def test_one_wire_learns_single_and_two_phase_patterns(self):
        for model in ("gn27","window"):
            for slots in ([0],[0,3,5],[0,2,5,7]):
                with self.subTest(model=model,slots=slots):
                    d=run(world_beats(slots,ticks=640),ticks=640,model=model)
                    self.assertTrue(late_success(d,32,640),d["error"][-20:])
    def test_switch_acquires_new_pattern(self):
        for model in ("gn27","window"):
            with self.subTest(model=model):
                d=compare_switch(model)
                self.assertEqual(d["late_errors"],0)
                self.assertEqual(d["world_last_lap"],d["predicted_last_lap"])
    def test_nine_ring_is_different_from_window(self):
        native=compare_nine_ring("gn27",trace_var=True)
        control=compare_nine_ring("window")
        self.assertGreater(native["errors_in_second_half"],0)
        self.assertEqual(control["errors_in_second_half"],0)
        self.assertIn("variance_cold_samples",native)


class GNSubstrate(unittest.TestCase):
    def test_nine_relay_forced_damp_does_not_fix_leak(self):
        from variance_branch import n9
        d=n9()
        self.assertEqual(d["native"]["late_errors"],10)
        self.assertEqual(d["native"]["variance_at_or_below_0_1"],0)
        self.assertEqual(d["force_all_damp"]["late_errors"],10)
        self.assertEqual(d["simple_window"]["late_errors"],0)
    def test_autonomous_clock_is_gn_only(self):
        from variance_branch import clock
        result=clock()
        self.assertEqual(result["gn27"]["beat_count"],6)
        self.assertEqual(result["window"]["beat_count"],0)

if __name__=="__main__":unittest.main()
