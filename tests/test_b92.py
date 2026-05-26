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
    bob_bits = [1, 1, 0, 0] # 1 means conclusive result

    # If Bob measured 1 in X (0th qubit), he knows Alice sent |0> (0)
    # If Bob measured 1 in Z (1st qubit), he knows Alice sent |+> (1)

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_bits)

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

    # In B92, if there is no noise, the sifted keys should match perfectly
    assert key_a == key_b
    assert len(key_a) > 0 # With 100 bits, we should get some conclusive results (~25%)
