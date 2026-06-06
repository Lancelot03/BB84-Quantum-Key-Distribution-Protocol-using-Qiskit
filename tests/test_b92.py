import pytest
from core.b92 import B92Protocol
from qiskit_aer import Aer

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
    # Bob measures in Z basis. If he gets 1 (i.e. |1>), he knows Alice didn't send |0> (0), so she sent |+> (1).
    # Bob measures in X basis. If he gets 1 (i.e. |->), he knows Alice didn't send |+> (1), so she sent |0> (0).
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'Z', 'Z', 'X']
    bob_bits = [1, 1, 0, 0] # Conclusive, Conclusive, Inconclusive, Inconclusive

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_bits)

    assert key_a == [0, 1]
    assert key_b == [0, 1]
    assert indices == [0, 1]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = Aer.get_backend('qasm_simulator')
    n = 50

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # In B92, when Bob gets a conclusive result, it MUST match Alice's bit (if no noise)
    assert key_a == key_b
    # Sifted key should be roughly n/4 in length (50% Bob chooses right basis, 50% he gets 1)
    assert len(key_a) > 0
