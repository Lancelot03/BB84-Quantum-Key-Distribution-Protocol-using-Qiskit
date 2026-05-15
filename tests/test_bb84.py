import pytest
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
