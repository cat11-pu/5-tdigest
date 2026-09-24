"""把 sample/latency.json 跑一遍，打印验收面（两个子系统）。"""
import json
import os
import sys

from summary import CompressedDigest
from tdigest import Digest


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("sample", "latency.json")
    with open(path, encoding="utf-8") as handle:
        spec = json.load(handle)
    exact = Digest()
    for value in spec["samples"]:
        exact.add(value)
    digest = CompressedDigest(spec["bucket_limit"])
    for value in spec["samples"]:
        digest.add(value)
    rows = [(q, round(digest.percentile(q), 2), round(abs(digest.percentile(q) - exact.percentile(q)), 2))
            for q in spec["quantiles"]]
    print("分位估计（分位, 估计值, 偏差） =", rows)
    print("桶数 =", digest.bucket_count())
    print("桶上限 =", spec["bucket_limit"])
    small = CompressedDigest(spec["bucket_limit"])
    for value in spec["small_sample"]:
        small.add(value)
    small_exact = Digest()
    for value in spec["small_sample"]:
        small_exact.add(value)
    print("小样本与精确值一致 =", small.percentile(0.5) == small_exact.percentile(0.5))
    print("小样本精确中位数 =", small_exact.percentile(0.5))
    print("样本数 =", len(spec["samples"]))
    print("最大偏差 =", max(row[2] for row in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
