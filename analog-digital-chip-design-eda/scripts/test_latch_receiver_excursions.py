import unittest
import json
import numpy as np
from analyze_latch_receiver_excursions import excursion_events


class ExcursionTests(unittest.TestCase):
    def test_intervals_include_boundary_events_and_keep_rails_legal(self):
        values=np.array([-.1,0,1.8,1.9,2,1.8,-.05])
        events=excursion_events(np.arange(7)*1e-9,values)
        self.assertEqual(len(events),3)
        json.dumps(events)
        self.assertEqual([e["peak_index"] for e in events],[4,0,6])
        self.assertEqual(events[0]["bracketing_start_ns"],2)
        self.assertEqual(events[0]["bracketing_end_ns"],5)
        self.assertEqual(excursion_events(np.array([0,1]),np.array([0,1.8])),[])


if __name__=="__main__":
    unittest.main()
