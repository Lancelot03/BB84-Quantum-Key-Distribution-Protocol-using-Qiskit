import pytest
from core.b92 import B92Protocol
from qiskit_aer import AerSimulator

def test_b92_generate_bits():
    protocol = B92Protocol()
    bits = protocol.generate_bits(10)
    assert len(bits) == 10
    assert all(bit in [0, 1] for bit in bits)

def test_b92_sift():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'Z', 'Z', 'X']
    bob_results = [1, 1, 0, 0]
    # Index 0: Alice 0 (|0>), Bob X (measure in {|+>, |->}). If Bob gets 1 (|->), it's conclusive. key_b=0
    # Index 1: Alice 1 (|+>), Bob Z (measure in {|0>, |1>}). If Bob gets 1 (|1>), it's conclusive. key_b=1

    key_a, key_b, indices = protocol.sift(["B92"]*4, bob_bases, alice_bits, bob_results)

    assert key_a == [0, 1]
    assert key_b == [0, 1]
    assert indices == [0, 1]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 100

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(["B92"]*n, bob_bases, alice_bits, bob_results)

    assert len(key_a) > 0
    assert key_a == key_b
