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
    # In B92, Bob only keeps bits where he got "1"
    # Alice sends 0 as |0>, 1 as |+>
    # If Alice sends 0 (|0>) and Bob measures in X, he has 50% chance of getting 1.
    # If he gets 1 in X, he knows Alice MUST have sent 0.
    alice_bits = [0, 1, 0, 1]
    bob_bases = ['X', 'Z', 'Z', 'X']
    bob_results = [1, 1, 0, 0] # Conclusive results for the first two

    sifted_a, sifted_b, indices = protocol.sift(alice_bits, bob_bases, bob_results)

    # Bob result 1 in X -> Bob knows Alice sent 0
    # Bob result 1 in Z -> Bob knows Alice sent 1
    assert sifted_a == [0, 1]
    assert sifted_b == [0, 1]
    assert indices == [0, 1]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    n = 100

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bits, bob_bases, bob_results)

    # In B92 without Eve, keys should always match
    assert key_a == key_b
    # Sifting efficiency should be ~25% (0.5 chance of choosing right basis * 0.5 chance of getting 1)
    # Actually:
    # 50% chance Bob chooses basis DIFFERENT from Alice's encoding basis.
    # In those cases, 50% chance he gets 1.
    # Total = 0.5 * 0.5 = 0.25.
    assert len(key_a) > 0
