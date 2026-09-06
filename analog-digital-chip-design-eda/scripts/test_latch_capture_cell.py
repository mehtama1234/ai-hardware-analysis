import unittest
from run_sky130_decision_capture_cell import select_cell,CELL


class CaptureCellTests(unittest.TestCase):
    def test_cell_selection_rejects_ambiguous_or_changed_interface(self):
        cell=f".subckt {CELL} CLK D VGND VNB VPB VPWR Q\n"+"\n".join(
            f"X{i} d g s b model w=1 l=1" for i in range(24))+"\n.ends\n"
        self.assertEqual(select_cell(cell),cell)
        for invalid in (cell+cell,cell.replace("CLK D","D CLK"),cell.replace("X23","* X23")):
            with self.assertRaises(ValueError):
                select_cell(invalid)


if __name__=="__main__":
    unittest.main()
