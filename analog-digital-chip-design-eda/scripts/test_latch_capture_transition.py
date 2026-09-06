import unittest
import numpy as np
from analyze_capture_data_transition import crossings


class DataTransitionTests(unittest.TestCase):
    def test_interpolation_and_direction(self):
        t=np.array([0,1,2])*1e-9; v=np.array([0,1.8,0])
        np.testing.assert_allclose(crossings(t,v,.9,True),[.5])
        np.testing.assert_allclose(crossings(t,v,.9,False),[1.5])

    def test_ringing_and_missing_edges_not_hidden(self):
        t=np.arange(5)*1e-9; v=np.array([0,1.8,0,1.8,0])
        np.testing.assert_allclose(crossings(t,v,.9,True),[.5,2.5])
        self.assertEqual(crossings(t,np.zeros(5),.9,True),[])
