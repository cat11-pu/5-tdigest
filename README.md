# tdigest

纯 Python 标准库的流式分位数（无第三方依赖，没有 pip 也能跑）。

## 用法

精确基线（留全部样本）：

    from tdigest import Digest
    digest = Digest()
    digest.add(42)
    digest.percentile(0.99)

压缩摘要（样本进桶，内存有界，桶数不超过 bucket_limit // 2）：

    from summary import CompressedDigest
    digest = CompressedDigest(bucket_limit=20)
    digest.add(42)
    digest.percentile(0.99)   # 在桶上按累计计数定位，返回桶内均值

指标服务（老接口 record / percentile 签名与行为不变）：

    from metrics import Metrics
    metrics = Metrics(bucket_limit=20)
    metrics.record(42)
    metrics.percentile(0.99)   # 老接口：精确值
    metrics.windows_report()   # 每 bucket_limit 条一个窗口，输出各窗口 p50/p90/p99

## 测试

    python3 -m unittest discover -s tests -v

## 场景自检

    python3 check_sample.py
