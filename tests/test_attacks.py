import pytest
from core.bb84 import BB84Protocol
from core.attacks import InterceptResend, NoisyChannel
from core.stats import calculate_qber
from qiskit_aer import AerSimulator

def test_intercept_resend_impact():
    protocol = BB84Protocol()
    backend = AerSimulator()
    attack = InterceptResend()
    n = 100

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
    noise_level = 0.2
    attack = NoisyChannel(noise_level)
    n = 100

    alice_bits = protocol.generate_bits(n)
    alice_bases = protocol.generate_bases(n)
    encoded = protocol.encode(alice_bits, alice_bases)

    intercepted = attack.apply(encoded, backend)

    bob_bases = alice_bases
    bob_results = protocol.measure(intercepted, bob_bases, backend)

    qber = calculate_qber(alice_bits, bob_results)

    # Noisy channel with 0.2 noise level (depolarizing)
    # 20% of bits are affected.
    # Depolarizing means X, Y, or Z with 1/3 each.
    # X flip introduces error (bit flip).
    # Y flip introduces error (bit and phase flip).
    # Z flip does NOT introduce error in Z basis (phase flip only).
    # So if bases are Z, X and Y cause error. 2/3 * 0.2 = ~0.133.
    # If bases are X, X does NOT cause error? Wait.
    # Actually in BB84, X basis is |+>, |->. Z flip swap them. Y flip swap them. X flip does NOT swap them.
    # So in any basis, 2 out of 3 types of flips cause error.
    # 0.2 * 2/3 = 0.133.
    assert 0.05 < qber < 0.25
