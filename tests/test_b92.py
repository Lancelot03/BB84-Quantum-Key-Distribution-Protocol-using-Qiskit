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
    # Alice sends 0 as |0>, 1 as |+>
    # Bob measures in X-basis for 0, Z-basis for 1
    # Conclusive results:
    # Alice sends 1 (|+>), Bob measures in Z, gets 1.
    # Alice sends 0 (|0>), Bob measures in X, gets 1.
    alice_bits = [0, 1, 1, 0]
    bob_bases = ['Z', 'X', 'Z', 'X']
    bob_results = [0, 0, 1, 1] # 1 means conclusive

    # Result 2: Bob basis Z, result 1 -> Bob infers Alice sent 1
    # Result 3: Bob basis X, result 1 -> Bob infers Alice sent 0

    sifted_a, sifted_b, indices = protocol.sift(None, bob_bases, alice_bits, bob_results)

    assert indices == [2, 3]
    assert sifted_a == [1, 0]
    assert sifted_b == [1, 0]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = Aer.get_backend('qasm_simulator')
    n = 100 # Higher n because B92 is less efficient (25% vs 50%)

    alice_bits = protocol.generate_bits(n)
    encoded = protocol.encode(alice_bits)

    bob_bases = protocol.generate_bases(n)
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(None, bob_bases, alice_bits, bob_results)

    assert len(key_a) > 0
    assert key_a == key_b
