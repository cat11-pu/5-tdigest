"""metrics.py：指标聚合服务（老调用方按原签名用它）。"""
from __future__ import annotations

from tdigest import Digest


class Metrics:
    def __init__(self, bucket_limit: int = 20):
        self.limit = bucket_limit
        self.digest = Digest()
        self.windows = []

    def record(self, value: float) -> None:
        self.digest.add(value)

    def percentile(self, q: float) -> float:
        """老接口：直接取分位。"""
        return self.digest.percentile(q)

    def windows_report(self) -> list:
        raise NotImplementedError("按窗口出报告还没实现")
