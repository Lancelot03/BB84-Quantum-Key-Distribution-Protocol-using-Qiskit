import pytest
from core.bb84 import BB84Protocol
from core.attacks import InterceptResend, NoisyChannel
from qiskit_aer import AerSimulator

def test_intercept_resend():
    protocol = BB84Protocol()
    attack = InterceptResend(intercept_probability=1.0)
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
    n = 100

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
    assert 0.1 < qber < 0.3
