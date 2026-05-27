import pytest
from core.b92 import B92Protocol
from qiskit_aer import AerSimulator

def test_b92_generate_bits():
    protocol = B92Protocol()
    bits = protocol.generate_bits(10)
    assert len(bits) == 10
    assert all(bit in [0, 1] for bit in bits)

def test_b92_generate_bases():
    protocol = B92Protocol()
    bases = protocol.generate_bases(10)
    assert len(bases) == 10
    assert all(base in ['Z', 'X'] for base in bases)

def test_b92_sift():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'Z', 'Z', 'X']
    # If Alice sends 0 (|0>) and Bob measures X, he gets 0 or 1.
    # If Alice sends 1 (|+>) and Bob measures Z, he gets 0 or 1.
    bob_results = [1, 1, 0, 0] # Conclusive, Conclusive, Inconclusive, Inconclusive

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

    assert indices == [0, 1]
    assert key_a == [0, 1]
    # If Bob measured 1 in X, Alice must have sent 0
    # If Bob measured 1 in Z, Alice must have sent 1
    assert key_b == [0, 1]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 100

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    assert len(key_a) > 0
    assert key_a == key_b
