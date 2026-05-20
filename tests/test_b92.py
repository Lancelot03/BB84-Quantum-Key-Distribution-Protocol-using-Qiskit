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

def test_b92_sift_no_errors():
    protocol = B92Protocol()
    # Alice sends: 0 (|0>), 1 (|+>), 0 (|0>), 1 (|+>)
    alice_bits = [0, 1, 0, 1]
    # Bob measures in: X, Z, Z, X
    bob_bases = ['X', 'Z', 'Z', 'X']
    # Bob's results (conclusive where he gets 1)
    # i=0: Alice |0>, Bob measures X. Bob gets 1 with 50% prob. Let's assume he gets 1.
    # i=1: Alice |+>, Bob measures Z. Bob gets 1 with 50% prob. Let's assume he gets 1.
    # i=2: Alice |0>, Bob measures Z. Bob gets 0 with 100% prob.
    # i=3: Alice |+>, Bob measures X. Bob gets 0 with 100% prob.
    bob_results = [1, 1, 0, 0]

    key_a, key_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

    # Bob got 1 at indices 0 and 1.
    # index 0: Bob basis X -> Bob deduces Alice sent |0> (0). Alice sent 0.
    # index 1: Bob basis Z -> Bob deduces Alice sent |+> (1). Alice sent 1.
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

    # In B92 without noise, sifted keys should match perfectly
    assert key_a == key_b
    # Efficiency is roughly 25% (50% chance Bob chooses right basis, 50% chance he gets conclusive result if he does)
    # Wait, in B92 Bob chooses basis. If Alice sends |0> and Bob measures X, he gets |1> with 50% prob.
    # If Alice sends |+> and Bob measures Z, he gets |1> with 50% prob.
    # So 50% of the time they have different "bases" (one rectilinear, one diagonal),
    # and in those cases Bob has 50% chance of getting a conclusive result.
    # So efficiency is ~25%.
    assert len(key_a) > 0
