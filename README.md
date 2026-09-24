# tdigest

纯 Python 标准库的 tdigest（无第三方依赖，没有 pip 也能跑）。

## 用法

- `tdigest.Digest`：基线实现，留全部样本排序取分位。
- `summary.CompressedDigest(bucket_limit)`：压缩摘要，样本进桶（桶数不超 `bucket_limit`），
  分位按桶累计计数定位、返回桶内均值；样本数不超过桶上限时与精确值一致。
- `metrics.Metrics`：老接口 `record` / `percentile` 签名不变；新增 `windows_report()`，
  按固定窗口（每 `window_size` 条一个窗口）输出各窗口的 p50 / p90 / p99。

## 测试

    python3 -m unittest discover -s tests -v

## 场景自检

    python3 check_sample.py
