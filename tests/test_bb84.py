import pytest
from core.bb84 import BB84Protocol
from qiskit_aer import AerSimulator

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
    backend = AerSimulator()
    n = 20

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    bob_bases = protocol.generate_bases(n)
    bob_results, _ = protocol.measure(encoded, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    assert key_a == key_b

def test_bb84_zero_qubits():
    protocol = BB84Protocol()
    bits = protocol.generate_bits(0)
    bases = protocol.generate_bases(0)
    circuits = protocol.encode(bits, bases)
    sifted_a, sifted_b, indices = protocol.sift([], [], [], [])

    assert bits == []
    assert bases == []
    assert circuits == []
    assert sifted_a == []
    assert sifted_b == []
    assert indices == []

def test_bb84_encoding_circuits():
    from qiskit.quantum_info import Statevector
    protocol = BB84Protocol()

    # Bit 0 in Z-basis -> |0>
    circ_0_z = protocol.encode([0], ['Z'])[0]
    sv_0_z = Statevector.from_instruction(circ_0_z)
    assert sv_0_z.to_dict().get('0', 0) == 1.0

    # Bit 1 in Z-basis -> |1>
    circ_1_z = protocol.encode([1], ['Z'])[0]
    sv_1_z = Statevector.from_instruction(circ_1_z)
    assert sv_1_z.to_dict().get('1', 0) == 1.0

    # Bit 0 in X-basis -> |+>
    circ_0_x = protocol.encode([0], ['X'])[0]
    sv_0_x = Statevector.from_instruction(circ_0_x)
    assert abs(sv_0_x.data[0] - 1 / (2**0.5)) < 1e-5
    assert abs(sv_0_x.data[1] - 1 / (2**0.5)) < 1e-5

    # Bit 1 in X-basis -> |->
    circ_1_x = protocol.encode([1], ['X'])[0]
    sv_1_x = Statevector.from_instruction(circ_1_x)
    assert abs(sv_1_x.data[0] - 1 / (2**0.5)) < 1e-5
    assert abs(sv_1_x.data[1] - (-1 / (2**0.5))) < 1e-5
