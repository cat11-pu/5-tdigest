import unittest

from metrics import Metrics
from tdigest import Digest


class TestDigest(unittest.TestCase):
    def test_single_sample(self):
        digest = Digest()
        digest.add(7)
        self.assertEqual(digest.percentile(0.5), 7)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            Digest().percentile(0.5)

    def test_median_of_three(self):
        digest = Digest()
        for value in (1, 2, 3):
            digest.add(value)
        self.assertEqual(digest.percentile(0.5), 2)

    def test_merge_sets_flag(self):
        left, right = Digest(), Digest()
        left.merge(right)
        self.assertEqual(left.merges, 1)

    def test_metrics_old_interface(self):
        metrics = Metrics()
        metrics.record(5)
        self.assertEqual(metrics.percentile(1.0), 5)


if __name__ == "__main__":
    unittest.main()
