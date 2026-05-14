import pytest
from core.bb84 import BB84Protocol
from qiskit_aer import Aer

def test_bb84_generate_bits():
    protocol = BB84Protocol()
    bits = protocol.generate_bits(10)
    assert len(bits) == 10
    assert all(bit in [0, 1] for bit in bits)

def test_bb84_generate_bases():
    protocol = BB84Protocol()
    bases = protocol.generate_bases(10)
    assert len(bases) == 10
    assert all(base in ['Z', 'X'] for base in bases)

def test_bb84_sift():
    protocol = BB84Protocol()
    alice_bits = [0, 1, 0, 1]
    alice_bases = ['Z', 'Z', 'X', 'X']
    bob_bases = ['Z', 'X', 'X', 'Z']
    bob_bits = [0, 1, 0, 1]

    sifted_a, sifted_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_bits)

    assert sifted_a == [0, 0]
    assert sifted_b == [0, 0]
    assert indices == [0, 2]

def test_bb84_full_no_eve():
    protocol = BB84Protocol()
    backend = Aer.get_backend('qasm_simulator')
    n = 20

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    assert key_a == key_b
