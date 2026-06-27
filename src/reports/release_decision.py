from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class GateResult:
    name: str
    status: str
    critical: bool
    detail: str = ""


@dataclass(frozen=True)
class ReleaseDecision:
    decision: str
    passed_critical: bool
    critical_failures: list[str]
    warnings: list[str]
    gates: list[GateResult]

    def to_dict(self) -> dict:
        return asdict(self)


def decide_release(gates: list[GateResult]) -> ReleaseDecision:
    critical_failures = [g.name for g in gates if g.critical and g.status in {"HOLD", "NO-GO"}]
    hard_no = [g.name for g in gates if g.status == "NO-GO"]
    warnings = [g.name for g in gates if not g.critical and g.status in {"HOLD", "NO-GO", "SOFT-GO"}]
    if hard_no:
        decision = "NO-GO"
    elif critical_failures:
        decision = "HOLD"
    elif warnings:
        decision = "SOFT-GO"
    else:
        decision = "GO"
    return ReleaseDecision(
        decision=decision,
        passed_critical=not critical_failures and not hard_no,
        critical_failures=critical_failures,
        warnings=warnings,
        gates=gates,
    )


def default_framework_gates() -> list[GateResult]:
    return [
        GateResult("Data Gate", "GO", True, "Schema, quality and continuity checks are implemented."),
        GateResult("Pine Export Gate", "GO", True, "Diagnostic export schema validation is implemented."),
        GateResult("Parity Gate", "HOLD", True, "Requires real TradingView diagnostic exports for each strategy."),
        GateResult("No-Future-Leak Gate", "GO", True, "Prefix-stability smoke check is implemented in CI."),
        GateResult("MTF Gate", "SOFT-GO", True, "Confirmed HTF helper exists; real Pine MTF parity remains required."),
        GateResult("Walk-forward Gate", "GO", True, "Frozen-window walk-forward engine exists."),
        GateResult("Robustness Gate", "SOFT-GO", False, "Multi-symbol split exists; real data robustness remains required."),
        GateResult("Forward Reconciliation Gate", "SOFT-GO", False, "Timestamp/direction reconciliation exists; live alerts remain required."),
        GateResult("CI Gate", "GO", True, "CI runs compile, tests and smoke checks."),
        GateResult("Documentation Gate", "GO", False, "Roadmap and agent assignment are documented."),
    ]


def write_release_json(decision: ReleaseDecision, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(decision.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_release_markdown(decision: ReleaseDecision, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Release Decision",
        "",
        f"Decision: **{decision.decision}**",
        "",
        "## Critical Failures",
        "",
    ]
    if decision.critical_failures:
        lines.extend(f"- {item}" for item in decision.critical_failures)
    else:
        lines.append("- None")
    lines.extend(["", "## Warnings", ""])
    if decision.warnings:
        lines.extend(f"- {item}" for item in decision.warnings)
    else:
        lines.append("- None")
    lines.extend(["", "## Gates", ""])
    for gate in decision.gates:
        lines.append(f"- {gate.name}: {gate.status} - {gate.detail}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
