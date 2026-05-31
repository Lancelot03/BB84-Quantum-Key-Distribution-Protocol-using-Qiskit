import pytest
import random
from core.b92 import B92Protocol
from qiskit_aer import Aer

def test_b92_generate_bits():
    protocol = B92Protocol()
    bits = protocol.generate_bits(10)
    assert len(bits) == 10
    assert all(bit in [0, 1] for bit in bits)

def test_b92_sift():
    protocol = B92Protocol()
    alice_bits = [0, 1, 0, 1]
    alice_bases = ["B92"] * 4
    bob_bases = ['Z', 'X', 'X', 'Z']
    bob_results = [0, 1, 1, 0] # 1 means conclusive

    key_a, key_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    # My sift logic:
    # if bob_results[i] == 1:
    #     key_b_bit = 1 if bob_bases[i] == 'Z' else 0
    #     key_a.append(alice_bits[i])
    #     key_b.append(key_b_bit)

    # index 1: bob_results[1]=1, bob_bases[1]='X' -> key_b_bit = 0. key_a.append(alice_bits[1]) which is 1.
    # index 2: bob_results[2]=1, bob_bases[2]='X' -> key_b_bit = 0. key_a.append(alice_bits[2]) which is 0.
    assert key_a == [1, 0]
    assert key_b == [0, 0]
    assert indices == [1, 2]

def test_b92_full_no_eve():
    protocol = B92Protocol()
    backend = Aer.get_backend('qasm_simulator')
    n = 100

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    bob_bases = [random.choice(['Z', 'X']) for _ in range(n)]
    bob_results = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    assert len(key_a) > 0
    assert key_a == key_b
