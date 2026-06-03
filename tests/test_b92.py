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
    assert all(base == 'B92' for base in bases)

def test_b92_sift():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    alice_bases = ['B92'] * 4
    bob_bases = ['Z', 'Z', 'X', 'X']
    bob_results = [0, 1, 1, 0] # Conclusive results at index 1 and 2

    # index 1: Alice 1 (|+>), Bob Z. If Bob gets 1 in Z, Alice must have sent 1.
    # index 2: Alice 0 (|0>), Bob X. If Bob gets 1 in X, Alice must have sent 0.

    sifted_a, sifted_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    assert indices == [1, 2]
    assert sifted_a == [1, 0]
    assert sifted_b == [1, 0]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = Aer.get_backend('qasm_simulator')
    n = 100

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bob_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    # In B92, if no noise, key_a should always equal key_b
    assert key_a == key_b
    # Should have roughly 25% efficiency
    assert len(key_a) > 0
