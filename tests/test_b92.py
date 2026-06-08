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
    alice_bits = [0, 1, 0, 1]
    alice_bases = ['B92'] * 4
    bob_bases = ['X', 'Z', 'Z', 'X']
    bob_results = [1, 1, 0, 0] # Conclusive, Conclusive, Inconclusive, Inconclusive

    # Bob measures 1 in X -> Alice must have sent 0
    # Bob measures 1 in Z -> Alice must have sent 1

    sifted_a, sifted_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    assert indices == [0, 1]
    assert sifted_a == [0, 1]
    assert sifted_b == [0, 1]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = Aer.get_backend('qasm_simulator')
    n = 100

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    alice_bases = ['B92'] * n
    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    assert len(key_a) > 0
    assert key_a == key_b
