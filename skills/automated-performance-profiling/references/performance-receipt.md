# Performance Profiling and Mitigation Receipt

Use this template after a profiling and optimization batch. Attach raw benchmark data and sanitized profiles where appropriate.

| Field | Value |
|---|---|
| Authorization and owner | `<approver, scope, and deployment boundary>` |
| Repository and commit | `<repo>@<commit>` |
| Environment | `<OS, hardware, runtime, compiler, flags, dependencies>` |
| Workload | `<dataset, input distribution, concurrency, cache state>` |
| Measurement protocol | `<profiler, benchmark, warm-up, repetitions, clock, noise controls>` |
| Target metric and budget | `<latency/throughput/memory/CPU/cost target>` |
| Baseline | `<p50/p95/p99, throughput, memory, CPU, errors, variance>` |
| Bottleneck evidence | `<profile, trace, counter, query plan, allocation data, confidence>` |
| Mitigation | `<root cause, changed files, invariant, trade-offs>` |
| Correctness verification | `<focused tests, regression tests, full suite, build>` |
| Post-change results | `<same measurements, distribution comparison, significance/variance>` |
| Regression review | `<tail latency, memory, CPU, throughput, errors, cost, workload sensitivity>` |
| Tower route | `<not applicable, or preflight → source-of-truth → exhibits/proof → validate → generate → test → build → integrity → receipt>` |
| Benchmark gate | `<command, threshold, ratchet/exception policy>` |
| Residual risk | `<noise, profiler overhead, workload drift, untested paths>` |
| Rollback | `<revert commit, feature flag, configuration restoration>` |
| Release decision | `<pass, block, or escalate with reason>` |
| Next action | `<merge, deploy, monitor, retry, or revert>` |
