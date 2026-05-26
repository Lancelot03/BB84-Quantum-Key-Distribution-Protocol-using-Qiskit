import pytest
from core.bb84 import BB84Protocol
from core.attacks import InterceptResend, NoisyChannel
from core.stats import calculate_qber
from qiskit_aer import AerSimulator

def test_intercept_resend_impact():
    protocol = BB84Protocol()
    backend = AerSimulator()
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

    # For X and Z basis:
    # X noise flips bit in Z basis, not in X basis.
    # Z noise flips bit in X basis, not in Z basis.
    # Y noise flips bit in both Z and X basis.
    # Each noise type (X, Y, Z) occurs with probability noise_level / 3.
    # In Z basis: errors caused by X and Y noise. Total prob = 2/3 * noise_level.
    # In X basis: errors caused by Z and Y noise. Total prob = 2/3 * noise_level.
    # Expected QBER = 2/3 * noise_level.
    # With noise_level = 0.3, expected QBER = 0.2.

    assert 0.1 < qber < 0.3
