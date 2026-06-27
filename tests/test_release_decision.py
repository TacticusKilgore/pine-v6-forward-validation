from src.reports.release_decision import GateResult, decide_release, default_framework_gates


def test_release_decision_go_when_all_critical_green():
    gates = [GateResult("Data", "GO", True), GateResult("Docs", "GO", False)]
    decision = decide_release(gates)
    assert decision.decision == "GO"
    assert decision.passed_critical


def test_release_decision_holds_on_missing_critical_gate():
    gates = [GateResult("Parity", "HOLD", True), GateResult("Docs", "GO", False)]
    decision = decide_release(gates)
    assert decision.decision == "HOLD"
    assert not decision.passed_critical


def test_default_framework_returns_hold_until_real_exports_exist():
    decision = decide_release(default_framework_gates())
    assert decision.decision == "HOLD"
    assert "Parity Gate" in decision.critical_failures
