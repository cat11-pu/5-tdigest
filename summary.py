"""summary.py：压缩摘要（样本进桶，分位在桶上估计，不再留全量样本排序）。"""
from __future__ import annotations


def _merge_pair(left, right):
    mean_l, count_l = left
    mean_r, count_r = right
    count = count_l + count_r
    return ((mean_l * count_l + mean_r * count_r) / count, count)


class CompressedDigest:
    """桶化摘要：样本数不超过桶上限时逐样本一桶（结果与精确值一致）；
    超限后相邻桶两两并入，把桶数压回上限以内。"""

    def __init__(self, bucket_limit: int = 20):
        if bucket_limit < 1:
            raise ValueError("bucket_limit 至少为 1")
        self.limit = bucket_limit
        self.samples = []
        self._buckets = None

    def add(self, value: float) -> None:
        self.samples.append(value)
        self._buckets = None

    def _compress(self):
        if self._buckets is not None:
            return self._buckets
        buckets = [(value, 1) for value in sorted(self.samples)]
        if len(buckets) > self.limit:
            while len(buckets) >= self.limit and len(buckets) > 1:
                merged = [_merge_pair(buckets[i], buckets[i + 1])
                          for i in range(0, len(buckets) - 1, 2)]
                if len(buckets) % 2:
                    merged.append(buckets[-1])
                buckets = merged
        self._buckets = buckets
        return buckets

    def percentile(self, q: float) -> float:
        if not self.samples:
            raise ValueError("没有样本")
        buckets = self._compress()
        total = sum(count for _, count in buckets)
        if total <= self.limit:
            index = min(total - 1, int(q * (total - 1) + 0.5))
            return buckets[index][0]
        target = q * total
        cumulative = 0
        for mean, count in buckets:
            cumulative += count
            if cumulative >= target:
                return mean
        return buckets[-1][0]

    def bucket_count(self) -> int:
        return len(self._compress())
