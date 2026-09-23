#!/usr/bin/env python3
"""
verify_phase1.py - Validation script for Phase 1 (Clean Core BB84 Simulator)

Verifies:
1. Alice and Bob random bit and basis generation.
2. Quantum circuit generation/encoding using Qiskit.
3. Ideal channel execution, key sifting, and zero QBER in noiseless conditions.
4. Eavesdropper simulation (InterceptResend) introducing expected errors (QBER > 0).
"""

from core import BB84Protocol, InterceptResend, SimulationEngine

def verify_phase1():
    print("=== Phase 1 Verification: BB84 Simulator Core ===")

    # 1. Test Protocol Direct Component Methods
    bb84 = BB84Protocol()
    n = 20
    bits = bb84.generate_bits(n)
    a_bases = bb84.generate_alice_bases(n)
    b_bases = bb84.generate_bases(n)

    assert len(bits) == n, f"Expected {n} bits, got {len(bits)}"
    assert len(a_bases) == n, f"Expected {n} Alice bases, got {len(a_bases)}"
    assert len(b_bases) == n, f"Expected {n} Bob bases, got {len(b_bases)}"

    circuits = bb84.encode(bits, a_bases)
    assert len(circuits) == n, f"Expected {n} quantum circuits, got {len(circuits)}"
    print("✓ Bit & Basis Generation and Quantum Circuit Encoding verified.")

    # 2. Test Ideal Engine Execution (No Eavesdropper)
    engine = SimulationEngine()
    num_qubits = 100
    res_ideal = engine.run(bb84, n=num_qubits, attack=None)

    assert res_ideal["protocol_name"] == "BB84"
    assert res_ideal["qber"] == 0.0, f"Expected 0% QBER in ideal channel, got {res_ideal['qber']}"
    assert res_ideal["is_secure"] is True
    assert len(res_ideal["key_a"]) > 0, "Sifted key should not be empty"
    assert res_ideal["key_a"] == res_ideal["key_b"], "Alice and Bob keys must match in ideal channel"
    print(f"✓ Ideal Channel Run verified: {len(res_ideal['key_a'])} bits sifted, QBER = {res_ideal['qber']*100:.2f}%.")

    # 3. Test Eavesdropper Attack (InterceptResend)
    attack = InterceptResend(intercept_probability=1.0)
    res_attack = engine.run(bb84, n=200, attack=attack)

    print(f"✓ Eavesdropped Channel Run verified: Sifted Key Length = {len(res_attack['key_a'])}, QBER = {res_attack['qber']*100:.2f}%, Security Status = {res_attack['security_status']}.")
    assert res_attack["qber"] > 0.0, "Expected non-zero QBER when Eve intercepts all qubits"

    print("\n🎉 Phase 1 All Validations Passed Successfully!")

if __name__ == "__main__":
    verify_phase1()
