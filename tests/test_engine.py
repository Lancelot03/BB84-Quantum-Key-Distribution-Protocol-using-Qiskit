import pytest
from core import BB84Protocol, B92Protocol, InterceptResend, SimulationEngine

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(n=20)

    assert results['protocol_name'] == "BB84"
    assert len(results['alice_bits']) == 20
    assert results['qber'] == 0.0
    assert results['is_secure'] is True

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(n=100)

    assert results['protocol_name'] == "BB84"
    # Intercept-Resend should introduce ~25% QBER in BB84
    assert results['qber'] > 0

def test_engine_b92_no_eve():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(n=40)

    assert results['protocol_name'] == "B92"
    assert results['qber'] == 0.0
    assert results['is_secure'] is True

def test_callback():
    messages = []
    def callback(msg):
        messages.append(msg)

    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    engine.run(n=10, callback=callback)

    assert len(messages) > 0
    assert any("Starting" in m for m in messages)
    assert any("complete" in m for m in messages)
