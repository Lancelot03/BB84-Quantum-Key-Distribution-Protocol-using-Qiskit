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

def test_b92_encode():
    protocol = B92Protocol()
    bits = [0, 1]
    circuits = protocol.encode(bits)
    assert len(circuits) == 2
    # Circuit 0 should be |0> (empty circuit is |0>)
    # Circuit 1 should have an H gate
    assert 'h' in circuits[1].count_ops()
    assert 'h' not in circuits[0].count_ops()

def test_b92_sift():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'Z', 'Z', 'X']
    bob_bits = [1, 1, 0, 0] # Conclusive if 1

    sifted_a, sifted_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_bits)

    # Bob measured 1 in X (index 0) -> Alice sent |0> (bit 0)
    # Bob measured 1 in Z (index 1) -> Alice sent |+> (bit 1)
    assert sifted_a == [0, 1]
    assert sifted_b == [0, 1]
    assert indices == [0, 1]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 50

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # In B92 without noise, whenever Bob gets a conclusive result,
    # he should be able to correctly infer Alice's bit.
    assert key_a == key_b
    assert len(key_a) > 0 # Probability of 0 conclusive results in 50 trials is very low (0.75^50)
