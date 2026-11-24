"""Evolve runner for the forked colony.

Cycles measure the current surfaces, propose one safe knob mutation,
re-measure, and keep only when the trial window is strictly better
and the twin control does not lead.

Does not touch the independent verifier. Does not rewrite free-form code.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .knobs import KNOBS, as_dict, get_knob

ROOT = Path(__file__).resolve().parent.parent
SOCIETY = ROOT / "society"
DATA = ROOT / "data"
CONTROL = ROOT / "control"


def _ensure_dirs() -> None:
    for p in (SOCIETY, DATA, CONTROL):
        p.mkdir(parents=True, exist_ok=True)


def run_seed_measurement(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Placeholder measurement. Replace with real queen runs on a fixed seed set."""
    knobs = as_dict(overrides)
    # Stub metrics that the real loop will fill from cluster maps + verifier.
    return {
        "knobs": knobs,
        "load_bearing_coverage": 1.0,
        "residual_risk_visible": True,
        "cost_usd": 0.09,
        "false_positive_rate": 0.0,
        "verifier_ok": True,
    }


def propose_one_mutation(current: dict[str, Any]) -> tuple[str, Any] | None:
    """Closed-set proposal. In the real loop this comes from a Hive-style chooser."""
    # Example: try raising escalation cap if it is still at default.
    name = "escalation_max_claims"
    current_val = current.get(name, get_knob(name))
    if current_val < KNOBS[name].max_val:
        return name, current_val + 1
    return None


def better(trial: dict[str, Any], baseline: dict[str, Any]) -> bool:
    """Strict improvement on the chosen metric. Adjust when real benches exist."""
    if not trial.get("verifier_ok") or not baseline.get("verifier_ok"):
        return False
    # Prefer higher coverage at equal or lower cost, or lower residual with no false-positive rise.
    if trial["load_bearing_coverage"] > baseline["load_bearing_coverage"] and trial["cost_usd"] <= baseline["cost_usd"]:
        return True
    if trial["false_positive_rate"] < baseline["false_positive_rate"] and trial["load_bearing_coverage"] >= baseline["load_bearing_coverage"]:
        return True
    return False


def evolve_once(state: dict[str, Any]) -> dict[str, Any]:
    baseline = run_seed_measurement(state.get("overrides"))
    proposal = propose_one_mutation(baseline["knobs"])
    if not proposal:
        state.setdefault("outcomes", []).append({"result": "no_proposal"})
        return state

    name, new_val = proposal
    trial_overrides = dict(state.get("overrides") or {})
    trial_overrides[name] = new_val
    trial = run_seed_measurement(trial_overrides)

    # Twin: control runs with no mutation.
    control = run_seed_measurement({})

    kept = better(trial, baseline) and not better(control, trial)
    outcome = {
        "knob": name,
        "from": baseline["knobs"].get(name),
        "to": new_val,
        "kept": kept,
        "baseline": baseline,
        "trial": trial,
        "control": control,
    }
    state.setdefault("outcomes", []).append(outcome)
    if kept:
        state.setdefault("overrides", {})[name] = new_val
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="Colony evolve runner")
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--offline", default="false")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    _ensure_dirs()
    state_path = DATA / "evolve_state.json"
    state: dict[str, Any] = {}
    if state_path.exists():
        state = json.loads(state_path.read_text())

    if args.status:
        print(json.dumps({"overrides": state.get("overrides"), "last_outcomes": state.get("outcomes", [])[-5:]}, indent=2))
        return

    for _ in range(args.cycles):
        state = evolve_once(state)

    state_path.write_text(json.dumps(state, indent=2))
    (SOCIETY / "LEARNING.md").write_text(
        "# Learning loop (stub)\n\n"
        "Outcomes are recorded in data/evolve_state.json.\n"
        "Keeps require trial better than baseline and twin not leading.\n"
        "Not AGI. Human authorize still required for durable accepts.\n"
    )
    print(json.dumps({"cycles": args.cycles, "overrides": state.get("overrides"), "outcomes": len(state.get("outcomes", []))}, indent=2))


if __name__ == "__main__":
    main()
