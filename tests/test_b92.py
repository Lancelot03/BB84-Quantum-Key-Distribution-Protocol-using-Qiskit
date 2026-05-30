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
    bob_bases = ['X', 'Z', 'Z', 'X'] # X means Bob measures in {|+>, |->}, Z means {|0>, |1>}
    bob_results = [1, 1, 0, 0] # Conclusive results for first two

    # If Bob measures 1 in X, he got |->, so Alice sent |0> (bit 0)
    # If Bob measured 1 in Z, he got |1>, so Alice sent |+> (bit 1)

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

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

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # In B92, if no noise, key_a should match key_b
    assert key_a == key_b
    # Also check that we got some bits (probabilistically we should get ~25% of n)
    assert len(key_a) > 0
