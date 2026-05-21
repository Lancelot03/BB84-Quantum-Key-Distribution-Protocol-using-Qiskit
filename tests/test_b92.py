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

def test_b92_sift():
    protocol = B92Protocol()
    # In B92: Alice sends 0 as |0>, 1 as |+>
    # Bob measures in Z (0) or X (1)
    # If Bob measures 1, it's conclusive.
    # Bob basis 'Z', Bob result 1 => Alice must have sent 1 (|+)
    # Bob basis 'X', Bob result 1 => Alice must have sent 0 (|0)

    alice_bits = [0, 1, 0, 1]
    bob_bases = ['Z', 'Z', 'X', 'X']
    bob_bits = [0, 1, 1, 0] # Conclusive results at indices 1 and 2

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_bits)

    assert key_a == [1, 0]
    assert key_b == [1, 0]
    assert indices == [1, 2]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 50

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # In B92 without noise, key_a should always match key_b
    assert key_a == key_b
    # Also check that some bits were actually sifted (probability of conclusive result is 1/4 per qubit)
    assert len(key_a) > 0
