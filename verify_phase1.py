#!/usr/bin/env python3
"""
verify_phase1.py - Validation script for Phase 1 BB84 Simulator core components.
"""

from core.bb84 import BB84Protocol
from core.attacks import InterceptResend
from core.stats import calculate_qber
from core.engine import SimulationEngine

def verify_phase1_bb84():
    print("=== Phase 1 BB84 Simulator Verification ===")

    # 1. Instantiate BB84 protocol
    protocol = BB84Protocol()
    assert protocol.name == "BB84", "Protocol name must be BB84"
    print("[✓] BB84 Protocol initialized successfully.")

    # 2. Bit and Basis Generation
    n = 100
    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_alice_bases(n)
    bob_bases = protocol.generate_bases(n)

    assert len(alice_bits) == n, f"Expected {n} bits, got {len(alice_bits)}"
    assert len(alice_bases) == n, f"Expected {n} bases, got {len(alice_bases)}"
    assert len(bob_bases) == n, f"Expected {n} bases, got {len(bob_bases)}"
    assert all(b in [0, 1] for b in alice_bits), "Bits must be 0 or 1"
    assert all(b in ['Z', 'X'] for b in alice_bases), "Bases must be 'Z' or 'X'"
    print("[✓] Alice & Bob bit and basis generation validated.")

    # 3. Quantum Circuit Generation & Encoding
    circuits = protocol.encode(alice_bits, alice_bases)
    assert len(circuits) == n, f"Expected {n} circuits, got {len(circuits)}"
    print("[✓] Quantum circuit generation and encoding validated.")

    # 4. Ideal Measurement and Key Sifting (No Eavesdropper)
    bob_results, meas_circs = protocol.measure(circuits, bob_bases)
    key_a, key_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    qber_ideal = calculate_qber(key_a, key_b)
    assert qber_ideal == 0.0, f"Ideal QBER should be 0.0, got {qber_ideal}"
    print(f"[✓] Ideal Simulation & Sifting validated (Sifted Key Length: {len(key_a)}, QBER: {qber_ideal}).")

    # 5. Eavesdropper Attack Simulation (Intercept-Resend)
    attack = InterceptResend(intercept_probability=1.0)
    intercepted_circs, attack_info = attack.apply(circuits)
    bob_results_attack, _ = protocol.measure(intercepted_circs, bob_bases)
    key_a_attack, key_b_attack, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results_attack)
    qber_attack = calculate_qber(key_a_attack, key_b_attack)

    print(f"[✓] Intercept-Resend Attack Simulation validated (QBER with Eve: {qber_attack:.2%}).")
    assert qber_attack > 0.0, "Eavesdropper attack should introduce non-zero QBER"

    # 6. Full Engine Flow Execution
    engine = SimulationEngine()
    result = engine.run(protocol, n=100, attack=attack)
    assert "qber" in result and "key_a" in result and "key_b" in result
    print("[✓] SimulationEngine orchestration flow validated.")

    print("\nPhase 1 BB84 Simulator verification passed successfully!")

if __name__ == "__main__":
    verify_phase1_bb84()
