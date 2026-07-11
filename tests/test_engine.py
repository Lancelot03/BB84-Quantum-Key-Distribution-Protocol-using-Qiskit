import pytest
from core import BB84Protocol, B92Protocol, SimulationEngine, InterceptResend

def test_engine_bb84_no_attack():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    n = 20
    results = engine.run(protocol, n)

    assert results['protocol_name'] == "BB84"
    assert len(results['alice_bits']) == n
    assert len(results['alice_bases']) == n
    assert len(results['bob_bases']) == n
    assert len(results['bob_results']) == n
    assert len(results['alice_circuits']) == n
    assert len(results['bob_circuits']) == n
    assert results['qber'] == 0.0
    assert results['is_secure'] is True

def test_engine_b92_no_attack():
    engine = SimulationEngine()
    protocol = B92Protocol()
    n = 40
    results = engine.run(protocol, n)

    assert results['protocol_name'] == "B92"
    assert len(results['alice_bits']) == n
    # In B92, sifting efficiency is ~25%, so we should have some keys
    # but QBER should be 0 without attack
    assert results['qber'] == 0.0
    assert results['is_secure'] is True

def test_engine_bb84_intercept_resend():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    attack = InterceptResend(intercept_probability=1.0)
    n = 100
    results = engine.run(protocol, n, attack=attack)

    assert results['protocol_name'] == "BB84"
    # QBER should be around 25% with Intercept-Resend on BB84
    assert results['qber'] > 0.1
    assert results['is_secure'] is False

def test_engine_callback():
    messages = []
    def callback(msg, progress=None):
        messages.append(msg)

    engine = SimulationEngine()
    protocol = BB84Protocol()
    engine.run(protocol, 10, callback=callback)

    assert len(messages) > 0
    assert "Initializing BB84 simulation" in messages[0]
    assert "Simulation complete." in messages[-1]
