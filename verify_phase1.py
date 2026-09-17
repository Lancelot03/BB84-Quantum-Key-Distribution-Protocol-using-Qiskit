"""
Phase 1 BB84 Simulator Verification Script
Checks core BB84 functionality including basis generation, quantum circuit encoding,
key sifting, QBER error analysis, and eavesdropper (Intercept-Resend) attacks.
"""

from core.bb84 import BB84Protocol
from core.attacks import InterceptResend
from core.engine import SimulationEngine
from core.stats import calculate_qber, analyze_security

def test_bb84_ideal_flow():
    print("--- Testing Ideal BB84 Flow ---")
    engine = SimulationEngine()
    protocol = BB84Protocol()
    n_qubits = 100

    results = engine.run(protocol, n_qubits, attack=None)

    assert results["protocol_name"] == "BB84", "Protocol name mismatch"
    assert len(results["alice_bits"]) == n_qubits, "Alice bits count mismatch"
    assert len(results["alice_bases"]) == n_qubits, "Alice bases count mismatch"
    assert len(results["bob_bases"]) == n_qubits, "Bob bases count mismatch"
    assert len(results["bob_results"]) == n_qubits, "Bob results count mismatch"
    assert len(results["alice_circuits"]) == n_qubits, "Alice circuits count mismatch"
    assert len(results["bob_circuits"]) == n_qubits, "Bob circuits count mismatch"
    assert results["qber"] == 0.0, f"Expected 0.0 QBER without attack, got {results['qber']}"
    assert results["is_secure"] is True, "Expected simulation to be secure without eavesdropper"
    print("Ideal BB84 Flow PASSED.")

def test_bb84_eavesdropping_flow():
    print("--- Testing Eavesdropping (Intercept-Resend) Flow ---")
    engine = SimulationEngine()
    protocol = BB84Protocol()
    attack = InterceptResend(intercept_probability=1.0)
    n_qubits = 200

    results = engine.run(protocol, n_qubits, attack=attack)

    assert results["protocol_name"] == "BB84", "Protocol name mismatch"
    assert results["qber"] > 0.10, f"Expected QBER > 0.10 under full Intercept-Resend, got {results['qber']}"
    assert results["is_secure"] is False, "Expected security check to detect eavesdropping"
    assert results["eve_info_gain"] > 0.0, "Expected positive information gain for Eve"
    print(f"Eavesdropping Flow PASSED with QBER = {results['qber']:.2%}")

if __name__ == "__main__":
    test_bb84_ideal_flow()
    test_bb84_eavesdropping_flow()
    print("\nAll Phase 1 BB84 Simulator verification checks completed successfully!")
