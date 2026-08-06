import pytest
from core.bb84 import BB84Protocol
from core.attacks import InterceptResend, NoisyChannel
from qiskit_aer import AerSimulator

def test_intercept_resend():
    protocol = BB84Protocol()
    attack = InterceptResend()
    backend = AerSimulator()
    n = 100

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    intercepted, info = attack.apply(encoded, backend)

    bob_bases = alice_bases # Perfect basis matching to isolate Eve's effect
    bob_results, _ = protocol.measure(intercepted, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    errors = sum(a != b for a, b in zip(key_a, key_b))
    qber = errors / len(key_a) if key_a else 0

    # Intercept-Resend should introduce ~25% QBER in BB84
    assert 0.15 < qber < 0.45

def test_noisy_channel():
    protocol = BB84Protocol()
    noise_level = 0.2
    attack = NoisyChannel(noise_level)
    backend = AerSimulator()
    n = 200

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    noisy, info = attack.apply(encoded, backend)

    bob_bases = alice_bases
    bob_results, _ = protocol.measure(noisy, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    errors = sum(a != b for a, b in zip(key_a, key_b))
    qber = errors / len(key_a) if key_a else 0

    # QBER should be close to noise_level
    assert 0.1 <= qber <= 0.3

def test_intercept_resend_partial():
    protocol = BB84Protocol()
    intercept_prob = 0.5
    attack = InterceptResend(intercept_probability=intercept_prob)
    backend = AerSimulator()
    n = 200

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    intercepted, info = attack.apply(encoded, backend)
    assert info['info_gain'] == intercept_prob * 0.5

    bob_bases = alice_bases
    bob_results, _ = protocol.measure(intercepted, bob_bases, backend)

    key_a, key_b, _ = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

    errors = sum(a != b for a, b in zip(key_a, key_b))
    qber = errors / len(key_a) if key_a else 0

    # Expected QBER: intercept_prob * 0.25 (which is 0.5 * 0.25 = 0.125)
    assert 0.05 < qber < 0.20
