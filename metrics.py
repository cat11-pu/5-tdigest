"""metrics.py：指标聚合服务（老调用方按原签名用它）。"""
from __future__ import annotations

from summary import CompressedDigest
from tdigest import Digest


class Metrics:
    def __init__(self, bucket_limit: int = 20, window_size: int = 10):
        self.limit = bucket_limit
        self.window_size = window_size
        self.digest = Digest()
        self.windows = []
        self._current = []

    def record(self, value: float) -> None:
        self.digest.add(value)
        self._current.append(value)
        if len(self._current) >= self.window_size:
            self.windows.append(self._current)
            self._current = []

    def percentile(self, q: float) -> float:
        """老接口：直接取分位。"""
        return self.digest.percentile(q)

    def windows_report(self) -> list:
        """按固定窗口（每 window_size 条一个窗口）输出每个窗口的 p50 / p90 / p99。"""
        windows = self.windows + ([self._current] if self._current else [])
        report = []
        for index, window in enumerate(windows):
            digest = CompressedDigest(self.limit)
            for value in window:
                digest.add(value)
            report.append({
                "window": index,
                "count": len(window),
                "p50": digest.percentile(0.5),
                "p90": digest.percentile(0.9),
                "p99": digest.percentile(0.99),
            })
        return report
