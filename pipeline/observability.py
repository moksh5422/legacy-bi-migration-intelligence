from __future__ import annotations

import time
from contextlib import contextmanager


@contextmanager
def measure(step: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[telemetry] step={step} latency_ms={elapsed_ms:.2f}")
