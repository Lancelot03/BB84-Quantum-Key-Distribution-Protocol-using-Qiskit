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
from core import bb84

def test_generate_alice_bits_and_bases():
    n = 10
    bits, bases = bb84.generate_alice_bits_and_bases(n)
    assert len(bits) == n
    assert len(bases) == n
    assert all(b in [0, 1] for b in bits)
    assert all(b in ['Z', 'X'] for b in bases)

def test_encode_qubits():
    bits = [0, 1]
    bases = ['Z', 'X']
    circuits = bb84.encode_qubits(bits, bases)
    assert len(circuits) == 2
    for qc in circuits:
        assert qc.num_qubits == 1

def test_sift_keys():
    alice_bases = ['Z', 'X', 'Z']
    bob_bases = ['Z', 'Z', 'Z']
    alice_bits = [0, 1, 0]
    bob_bits = [0, 0, 0]
    s_alice, s_bob, indices = bb84.sift_keys(alice_bases, bob_bases, alice_bits, bob_bits)
    assert s_alice == [0, 0]
    assert s_bob == [0, 0]
    assert indices == [0, 2]

def test_measure_qubits():
    # Test simple Z-basis measurement
    bits = [0, 1]
    bases = ['Z', 'Z']
    circuits = bb84.encode_qubits(bits, bases)
    bob_bases = ['Z', 'Z']
    results = bb84.measure_qubits(circuits, bob_bases)
    assert results == bits
