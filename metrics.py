"""metrics.py：指标聚合服务（老调用方按原签名用它）。"""
from __future__ import annotations

from summary import CompressedDigest
from tdigest import Digest


class Metrics:
    def __init__(self, bucket_limit: int = 20):
        self.limit = bucket_limit
        self.digest = Digest()
        self.windows = []

    def record(self, value: float) -> None:
        self.digest.add(value)
        if not self.windows or self.windows[-1].total >= self.limit:
            self.windows.append(CompressedDigest(self.limit))
        self.windows[-1].add(value)

    def percentile(self, q: float) -> float:
        """老接口：直接取分位。"""
        return self.digest.percentile(q)

    def windows_report(self) -> list:
        """按固定窗口（每 self.limit 条一个窗口）输出每个窗口的 p50 / p90 / p99。"""
        report = []
        for digest in self.windows:
            if digest.total == 0:
                continue
            report.append({
                "p50": digest.percentile(0.5),
                "p90": digest.percentile(0.9),
                "p99": digest.percentile(0.99),
            })
        return report
