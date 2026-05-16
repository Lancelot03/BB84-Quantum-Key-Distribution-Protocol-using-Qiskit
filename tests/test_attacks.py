import pytest
from core.bb84 import BB84Protocol
from core.attacks import InterceptResend, NoisyChannel
from core.stats import calculate_qber
from qiskit_aer import Aer

def test_intercept_resend_impact():
    protocol = BB84Protocol()
    backend = Aer.get_backend('qasm_simulator')
    attack = InterceptResend()
    n = 200

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    intercepted = attack.apply(encoded, backend)

    bob_bases = alice_bases # Perfect basis matching to isolate Eve's impact
    bob_results = protocol.measure(intercepted, bob_bases, backend)

    qber = calculate_qber(alice_bits, bob_results)

    # Intercept-resend should introduce ~25% error if bases match
    # Since we matched all bases, if Eve chooses wrong basis (50% of time),
    # she introduces 50% error on those. 0.5 * 0.5 = 0.25.
    assert 0.15 < qber < 0.35

def test_noisy_channel_impact():
    protocol = BB84Protocol()
    backend = Aer.get_backend('qasm_simulator')
    noise_level = 0.5
    attack = NoisyChannel(noise_level)
    n = 200

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    intercepted = attack.apply(encoded, backend)

    bob_bases = alice_bases
    bob_results = protocol.measure(intercepted, bob_bases, backend)

    qber = calculate_qber(alice_bits, bob_results)

    # Noisy channel with 0.5 noise level should introduce ~25% error if bases match
    # Wait, NoisyChannel applies X gate.
    # In Z basis, X flips 0 to 1 and 1 to 0. 100% error if applied.
    # So if noise_level is 0.5, we expect 50% error in Z basis.
    # In X basis, X gate maps |+> to |+> and |-> to -|->.
    # |+> = (|0>+|1>)/sqrt(2). X|+> = (|1>+|0>)/sqrt(2) = |+>. No error.
    # |-> = (|0>-|1>)/sqrt(2). X|-> = (|1>-|0>)/sqrt(2) = -|->. No bit error (measurement gives 1 for both).
    # Wait, Bob measures in X basis by applying H and then measuring in Z.
    # H|-> = |1>. H(-|->) = -|1>. Measurement gives 1. No bit error.
    # So X noise ONLY affects Z basis in BB84.
    # Since n=200, ~100 are Z basis. ~50 of those get X gate. ~50 errors.
    # Total QBER = 50 / 200 = 0.25.
    assert 0.15 < qber < 0.35

def test_calculate_qber():
    key_a = [0, 1, 0, 1]
    key_b = [0, 1, 1, 1]
    qber = calculate_qber(key_a, key_b)
    assert qber == 0.25

    assert calculate_qber([], []) == 0.0
