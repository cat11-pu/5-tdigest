"""summary.py：压缩摘要（样本进桶的流式分位数，内存有界）。

设计要点：
- 样本先进入缓冲区，缓冲区满（达到 bucket_limit）才落桶；
- 落桶时相邻两个样本并为一个桶，桶保存 (均值, 计数)；
- 桶数超过 bucket_limit // 2 时，相邻桶两两合并，直到不超限；
- 样本数未触发压缩时，分位结果与精确值完全一致。
"""
from __future__ import annotations


class CompressedDigest:
    def __init__(self, bucket_limit: int = 20):
        if bucket_limit < 2:
            raise ValueError("bucket_limit 至少为 2")
        self.limit = bucket_limit
        self.buckets = []  # [(均值, 计数)]，按均值升序
        self.pending = []  # 未落桶的原始样本
        self.total = 0
        self.merged = False

    def add(self, value: float) -> None:
        self.pending.append(value)
        self.total += 1
        if len(self.pending) >= self.limit:
            self._flush()

    def _flush(self) -> None:
        """缓冲区满：排序后相邻两个样本并成一个桶。"""
        ordered = sorted(self.pending)
        self.pending = []
        for index in range(0, len(ordered) - 1, 2):
            self.buckets.append(((ordered[index] + ordered[index + 1]) / 2, 2))
        if len(ordered) % 2:
            self.buckets.append((ordered[-1], 1))
        self.buckets.sort(key=lambda bucket: bucket[0])
        self.merged = True
        self._compress()

    def _compress(self) -> None:
        """桶数超限时，最接近的相邻桶两两合并。"""
        cap = max(1, self.limit // 2)
        while len(self.buckets) > cap:
            merged = []
            for index in range(0, len(self.buckets) - 1, 2):
                merged.append(self._merge(self.buckets[index], self.buckets[index + 1]))
            if len(self.buckets) % 2:
                merged.append(self.buckets[-1])
            self.buckets = merged

    @staticmethod
    def _merge(left, right):
        mean_left, count_left = left
        mean_right, count_right = right
        count = count_left + count_right
        return ((mean_left * count_left + mean_right * count_right) / count, count)

    def percentile(self, q: float) -> float:
        if self.total == 0:
            raise ValueError("没有样本")
        if not self.merged:
            # 从未压缩过：与精确算法完全一致。
            ordered = sorted(self.pending)
            index = min(len(ordered) - 1, int(q * (len(ordered) - 1) + 0.5))
            return ordered[index]
        buckets = sorted(self.buckets + [(value, 1) for value in self.pending],
                         key=lambda bucket: bucket[0])
        threshold = q * self.total
        cumulative = 0
        for mean, count in buckets:
            cumulative += count
            if cumulative >= threshold:
                return mean
        return buckets[-1][0]

    def bucket_count(self) -> int:
        """已压缩落桶的数量（不含缓冲区里未落桶的样本）。"""
        return len(self.buckets)
