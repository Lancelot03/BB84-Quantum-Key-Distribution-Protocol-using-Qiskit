import pytest
from core.b92 import B92Protocol
from core.stats import calculate_qber

def test_b92_full_no_eve():
    protocol = B92Protocol()
    n = 100
    alice_bits = protocol.generate_bits(n)
    encoded_qubits = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded_qubits, bob_bases)

    key_a, key_b, indices = protocol.sift(alice_bits, bob_bases, bob_results)

    # In B92 without noise/eve, keys should match perfectly
    assert len(key_a) == len(key_b)
    assert key_a == key_b

    qber = calculate_qber(key_a, key_b)
    assert qber == 0.0

def test_b92_efficiency():
    protocol = B92Protocol()
    n = 1000
    alice_bits = protocol.generate_bits(n)
    encoded_qubits = protocol.encode(alice_bits)
    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded_qubits, bob_bases)

    key_a, _, _ = protocol.sift(alice_bits, bob_bases, bob_results)

    # Efficiency should be around 25% for B92
    # Alice sends |0> or |+>. Bob measures in Z or X.
    # 4 cases:
    # Alice |0>, Bob Z: Bob measures 0 (1/4)
    # Alice |0>, Bob X: Bob measures 0 or 1 with 1/2 each (1/4) -> 1/8 chance for 1
    # Alice |+>, Bob Z: Bob measures 0 or 1 with 1/2 each (1/4) -> 1/8 chance for 1
    # Alice |+>, Bob X: Bob measures 0 (1/4)
    # Total chance for 1 is 1/8 + 1/8 = 1/4 = 25%
    efficiency = len(key_a) / n
    assert 0.15 < efficiency < 0.35
