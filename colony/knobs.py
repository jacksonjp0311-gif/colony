"""Closed set of safe knobs the evolve runner may propose.

No free-form code. No change to the independent verifier.
Queen still only reads the cluster map. No averaging.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Knob:
    name: str
    default: Any
    min_val: Any | None = None
    max_val: Any | None = None
    description: str = ""


# Safe, measurable parameters. Extend only with a test.
KNOBS: dict[str, Knob] = {
    "escalation_max_claims": Knob(
        name="escalation_max_claims",
        default=2,
        min_val=0,
        max_val=4,
        description="Max claims that may receive extra scouts after the coverage pass.",
    ),
    "single_source_penalty": Knob(
        name="single_source_penalty",
        default=1,
        min_val=0,
        max_val=2,
        description="How hard the judge treats a single-sourced load-bearing claim (0=ignore, 1=conditions, 2=hold).",
    ),
    "coverage_priority_boost": Knob(
        name="coverage_priority_boost",
        default=0,
        min_val=-10,
        max_val=10,
        description="Additive priority adjustment for load-bearing claims during allocation.",
    ),
}


def get_knob(name: str, overrides: dict[str, Any] | None = None) -> Any:
    """Return current value (default or override). Fails closed on unknown names."""
    if name not in KNOBS:
        raise KeyError(f"unknown knob: {name}")
    if overrides and name in overrides:
        return overrides[name]
    return KNOBS[name].default


def as_dict(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    return {k: get_knob(k, overrides) for k in KNOBS}
