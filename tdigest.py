"""tdigest：流式分位数（基线：留下全部样本再排序）。"""
from __future__ import annotations


class Digest:
    def __init__(self):
        self.samples = []
        self.merges = 0

    def add(self, value: float) -> None:
        self.samples.append(value)

    def percentile(self, q: float) -> float:
        if not self.samples:
            raise ValueError("没有样本")
        ordered = sorted(self.samples)
        index = min(len(ordered) - 1, int(q * (len(ordered) - 1) + 0.5))
        return ordered[index]

    def merge(self, other) -> None:
        self.samples.extend(other.samples)
        self.merges += 1

    def bucket_count(self) -> int:
        return len(self.samples)
