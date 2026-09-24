import json
import os
import unittest

from metrics import Metrics
from summary import CompressedDigest
from tdigest import Digest


def load_sample():
    path = os.path.join(os.path.dirname(__file__), "..", "sample", "latency.json")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


class TestCompressedDigest(unittest.TestCase):
    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            CompressedDigest().percentile(0.5)

    def test_small_sample_matches_exact(self):
        spec = load_sample()
        digest = CompressedDigest(spec["bucket_limit"])
        exact = Digest()
        for value in spec["small_sample"]:
            digest.add(value)
            exact.add(value)
        for q in (0.0, 0.25, 0.5, 0.9, 0.99, 1.0):
            self.assertEqual(digest.percentile(q), exact.percentile(q))

    def test_bucket_count_within_limit(self):
        spec = load_sample()
        digest = CompressedDigest(spec["bucket_limit"])
        for value in spec["samples"]:
            digest.add(value)
            self.assertLessEqual(digest.bucket_count(), spec["bucket_limit"])
        self.assertEqual(digest.bucket_count(), 10)

    def test_estimates_within_tolerance(self):
        spec = load_sample()
        digest = CompressedDigest(spec["bucket_limit"])
        exact = Digest()
        for value in spec["samples"]:
            digest.add(value)
            exact.add(value)
        expected = {0.5: (56.25, 5.75), 0.9: (116.25, 13.75), 0.99: (180.0, 70.0)}
        for q, (estimate, deviation) in expected.items():
            self.assertAlmostEqual(digest.percentile(q), estimate)
            self.assertAlmostEqual(abs(digest.percentile(q) - exact.percentile(q)), deviation)


class TestWindowsReport(unittest.TestCase):
    def test_windows_of_fixed_size(self):
        metrics = Metrics(bucket_limit=4)
        for value in range(1, 11):
            metrics.record(value)
        report = metrics.windows_report()
        self.assertEqual(len(report), 3)  # 4 + 4 + 2
        for row in report:
            self.assertEqual(sorted(row), ["p50", "p90", "p99"])
        self.assertEqual(report[0], {"p50": 1.5, "p90": 3.5, "p99": 3.5})
        self.assertEqual(report[1], {"p50": 5.5, "p90": 7.5, "p99": 7.5})
        self.assertEqual(report[2], {"p50": 10, "p90": 10, "p99": 10})

    def test_windows_match_exact_for_small_windows(self):
        metrics = Metrics(bucket_limit=20)
        for value in (1, 2, 3):
            metrics.record(value)
        report = metrics.windows_report()
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["p50"], 2)
        self.assertEqual(report[0]["p99"], 3)

    def test_empty_report(self):
        self.assertEqual(Metrics().windows_report(), [])


if __name__ == "__main__":
    unittest.main()
