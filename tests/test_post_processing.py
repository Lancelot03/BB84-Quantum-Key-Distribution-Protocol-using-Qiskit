import pytest
from core.reconciliation import CascadeReconciler
from core.privacy import PrivacyAmplifier

def test_cascade_reconciliation():
    reconciler = CascadeReconciler(block_size=4)
    alice_key = [1, 0, 1, 1, 0, 0, 1, 0]
    bob_key   = [1, 0, 0, 1, 0, 0, 1, 1] # 2 errors at indices 2 and 7

    corrected_bob, errors_fixed = reconciler.reconcile(alice_key, bob_key)

    # In this simplified one-pass version, it might not catch ALL errors if there are 2 in one block
    # but it should definitely do something.
    assert errors_fixed > 0
    # At index 2, parity of [1,0,1,1] is 1, [1,0,0,1] is 0 -> Should fix.
    assert corrected_bob[2] == 1

def test_privacy_amplification():
    amplifier = PrivacyAmplifier(compression_factor=0.5)
    key = [1, 0, 1, 1, 0, 0, 1, 0]

    amplified_key = amplifier.amplify(key)

    assert len(amplified_key) == 4
    # Deterministic check
    amplified_key_2 = amplifier.amplify(key)
    assert amplified_key == amplified_key_2

def test_privacy_amplification_different_keys():
    amplifier = PrivacyAmplifier(compression_factor=0.5)
    key_a = [1, 0, 1, 1, 0, 0, 1, 0]
    key_b = [1, 0, 1, 1, 0, 0, 1, 1]

    amp_a = amplifier.amplify(key_a)
    amp_b = amplifier.amplify(key_b)

    assert amp_a != amp_b
