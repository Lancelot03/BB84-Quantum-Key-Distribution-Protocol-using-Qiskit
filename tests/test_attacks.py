import pytest
from core import bb84, attacks, metrics

def test_intercept_resend():
    n = 20
    bits, bases = bb84.generate_alice_bits_and_bases(n)
    circuits = bb84.encode_qubits(bits, bases)
    intercepted, eve_bases = attacks.intercept_resend(circuits)

    assert len(intercepted) == n
    assert len(eve_bases) == n

    # Check that intercepted circuits are valid
    for qc in intercepted:
        assert qc.num_qubits == 1

def test_noisy_channel():
    n = 100
    # Use Z basis only for simpler verification of bit flips
    bits = [0, 1] * (n // 2)
    bases = ['Z'] * n
    circuits = bb84.encode_qubits(bits, bases)
    # High noise to ensure all bits are flipped
    noisy = attacks.noisy_channel(circuits, noise_level=1.0)

    bob_results = bb84.measure_qubits(noisy, bases)
    # Since it's all bit-flipped in Z basis, every bit should be different
    assert all(a != b for a, b in zip(bits, bob_results))

def test_calculate_qber():
    key_a = [0, 1, 0, 1]
    key_b = [0, 1, 1, 1]
    qber = metrics.calculate_qber(key_a, key_b)
    assert qber == 0.25

    assert metrics.calculate_qber([], []) == 0.0
