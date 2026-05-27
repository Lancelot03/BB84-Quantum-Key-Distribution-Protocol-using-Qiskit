import pytest
from core.bb84 import BB84Protocol
from core.attacks import InterceptResend, NoisyChannel
from core.stats import calculate_qber
from qiskit_aer import AerSimulator

def test_intercept_resend_impact():
    protocol = BB84Protocol()
    backend = AerSimulator()
    attack = InterceptResend()
    n = 200 # Increased for better statistics

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    intercepted = attack.apply(encoded, backend)

    bob_bases = alice_bases # Perfect basis matching to isolate Eve's impact
    bob_results = protocol.measure(intercepted, bob_bases, backend)

    qber = calculate_qber(alice_bits, bob_results)

    # Intercept-resend should introduce ~25% error if bases match
    assert 0.18 < qber < 0.32

def test_noisy_channel_impact():
    protocol = BB84Protocol()
    backend = AerSimulator()
    noise_level = 0.3
    attack = NoisyChannel(noise_level)
    n = 200

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    intercepted = attack.apply(encoded, backend)

    bob_bases = alice_bases
    bob_results = protocol.measure(intercepted, bob_bases, backend)

    qber = calculate_qber(alice_bits, bob_results)

    # Depolarizing noise: with prob p, apply X, Y, or Z.
    # X and Y cause bit flips. Z doesn't (in Z basis).
    # In X basis, Z and Y cause bit flips. X doesn't.
    # So each noise application has 2/3 chance of causing an error in any fixed basis.
    # Expected QBER = p * 2/3. For p=0.3, QBER ~ 0.2.
    assert 0.12 < qber < 0.28
