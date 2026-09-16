"""
Verification script for Phase 1 - Clean Core BB84 Simulator.
Verifies basis generation, quantum circuit generation, key sifting, QBER, and Eve attack simulation.
"""
from core import BB84Protocol, SimulationEngine, InterceptResend, NoisyChannel, PhotonNumberSplitting
from core.stats import calculate_qber

def main():
    print("=== Testing Phase 1 BB84 Protocol Features ===")

    # 1. BB84 Protocol direct tests
    protocol = BB84Protocol()
    n = 20

    bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_alice_bases(n)
    bob_bases = protocol.generate_bases(n)

    assert len(bits) == n, f"Expected {n} bits, got {len(bits)}"
    assert len(alice_bases) == n, f"Expected {n} Alice bases, got {len(alice_bases)}"
    assert len(bob_bases) == n, f"Expected {n} Bob bases, got {len(bob_bases)}"
    assert set(bits).issubset({0, 1}), "Bits must be 0 or 1"
    assert set(alice_bases).issubset({'Z', 'X'}), "Bases must be Z or X"
    assert set(bob_bases).issubset({'Z', 'X'}), "Bases must be Z or X"
    print("✔ Basis and bit generation passed.")

    # 2. Quantum Circuit encoding
    circuits = protocol.encode(bits, alice_bases)
    assert len(circuits) == n, "Encoded circuit count mismatch"
    assert circuits[0].num_qubits == 1, "Expected single qubit circuit"
    print("✔ Quantum circuit encoding passed.")

    # 3. Measurement without Eve (Ideal Channel)
    bob_results, meas_circs = protocol.measure(circuits, bob_bases)
    sifted_a, sifted_b, indices = protocol.sift(alice_bases, bob_bases, bits, bob_results)
    qber = calculate_qber(sifted_a, sifted_b)

    assert qber == 0.0, f"Ideal channel QBER should be 0.0, got {qber}"
    print(f"✔ Ideal simulation passed. Sifted key length: {len(sifted_a)}, QBER: {qber}")

    # 4. Simulation Engine run with InterceptResend attack
    engine = SimulationEngine()
    attack = InterceptResend(intercept_probability=1.0)
    res = engine.run(protocol=protocol, n=100, attack=attack)

    print(f"✔ Simulation with InterceptResend completed. QBER: {res['qber'] * 100:.2f}%, Security Status: {res['security_status']}")
    assert res["qber"] > 0.0, "Eavesdropping with probability 1.0 should induce QBER > 0"
    assert "key_a" in res and "key_b" in res, "Results missing key outputs"

    print("\nAll Phase 1 feature verifications completed successfully!")

if __name__ == "__main__":
    main()
