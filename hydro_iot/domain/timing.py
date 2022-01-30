from dataclasses import dataclass


@dataclass
class SprayTiming:
    duration_ms: int
    interval_ms: int
