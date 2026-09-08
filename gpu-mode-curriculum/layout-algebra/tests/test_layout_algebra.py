import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from layout_algebra import Layout2D, blocked_2d, row_major, xor_swizzled_2d


class LayoutAlgebraTests(unittest.TestCase):
    def test_row_major_inverse(self):
        layout = row_major(3, 5)
        self.assertEqual(layout.offset(2, 4), 14)
        self.assertEqual(layout.inverse()[0], (0, 0))

    def test_blocked_layout_is_bijective(self):
        layout = blocked_2d(8, 16, 4, 4)
        self.assertEqual(len(set(layout.offsets())), layout.size)
        self.assertEqual(layout.inverse()[layout.offset(5, 7)], (5, 7))

    def test_swizzle_is_bijective_and_self_consistent(self):
        layout = xor_swizzled_2d(8, 16, 4, 4)
        self.assertTrue(layout.check_bijection()["bijection"])
        self.assertEqual(len(layout.inverse()), 128)

    def test_blocked_rejects_tail_shape(self):
        with self.assertRaises(ValueError):
            blocked_2d(7, 16, 4, 4)

    def test_bounds_rejected(self):
        with self.assertRaises(IndexError):
            row_major(2, 2).offset(2, 0)


if __name__ == "__main__":
    unittest.main()
