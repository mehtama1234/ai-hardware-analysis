import unittest
import numpy as np
from analyze_latch_offset_sweeps import classify_hold, transition_bracket

class OffsetTests(unittest.TestCase):
    def test_conflicting_decisions_cannot_form_one_offset_bracket(self):
        rows=[{"input_diff_mv":x,"stable_receiver_decision":s} for x,s in
              ((12,"negative"),(12.5,"negative"),(12.5,"positive"),(13,"positive"))]
        self.assertIsNone(transition_bracket(rows))
        self.assertEqual(transition_bracket([rows[0],rows[3]]),[12,13])

    def test_actual_decision_does_not_require_correct_input_sign(self):
        low=np.array([0.01,0.02]); high=np.array([1.7,1.75])
        self.assertEqual(classify_hold(low,high,high,low),"negative")
        self.assertEqual(classify_hold(high,low,low,high),"positive")

    def test_unsettled_or_invalid_receiver_is_unresolved(self):
        low=np.array([0.01,0.02]); high=np.array([1.7,1.75])
        self.assertEqual(classify_hold(high,low,high,high),"unresolved")
        self.assertEqual(classify_hold(np.array([0.2,1.7]),low,low,high),"unresolved")
        empty=np.array([])
        self.assertEqual(classify_hold(empty,empty,empty,empty),"unresolved")

if __name__=="__main__":
    unittest.main()
