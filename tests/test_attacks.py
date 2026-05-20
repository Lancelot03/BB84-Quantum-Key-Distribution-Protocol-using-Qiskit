import pytest
from core.bb84 import BB84Protocol
from core.attacks import InterceptResend, NoisyChannel
from core.stats import calculate_qber
from qiskit_aer import Aer

def test_intercept_resend_impact():
    protocol = BB84Protocol()
    backend = Aer.get_backend('qasm_simulator')
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
    backend = Aer.get_backend('qasm_simulator')
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

    # Depolarizing noise with 0.2 noise level introduces errors
    # and we expect QBER to be around noise_level * (2/3) roughly
    # since Z flips affect Z basis, Y flips affect both, X flips affect X (in Alice's bases)
    # Actually, for Z-basis: X and Y flips cause error. (2/3 * noise_level)
    # For X-basis: Z and Y flips cause error. (2/3 * noise_level)
    # So total error rate is roughly 2/3 * noise_level = 0.133
    assert 0.05 < qber < 0.25
