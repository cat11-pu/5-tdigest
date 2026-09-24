import unittest

from metrics import Metrics
from summary import CompressedDigest
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


class TestCompressedDigest(unittest.TestCase):
    def test_small_sample_matches_exact(self):
        compressed, exact = CompressedDigest(20), Digest()
        for value in (10, 20, 30, 40, 50):
            compressed.add(value)
            exact.add(value)
        for q in (0.1, 0.4, 0.5, 0.9, 0.99):
            self.assertEqual(compressed.percentile(q), exact.percentile(q))

    def test_bucket_limit_respected(self):
        compressed = CompressedDigest(20)
        for value in range(40):
            compressed.add(value)
        self.assertLessEqual(compressed.bucket_count(), 20)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            CompressedDigest(20).percentile(0.5)

    def test_windows_report(self):
        metrics = Metrics(window_size=2)
        for value in (10, 20, 30, 40, 50):
            metrics.record(value)
        report = metrics.windows_report()
        self.assertEqual(len(report), 3)
        self.assertEqual(report[0]["count"], 2)
        self.assertEqual(report[0]["p50"], 20)
        self.assertEqual(report[2]["count"], 1)
        self.assertEqual(report[2]["p99"], 50)


if __name__ == "__main__":
    unittest.main()
