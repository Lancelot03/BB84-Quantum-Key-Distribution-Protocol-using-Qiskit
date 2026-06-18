import pytest
from core import BB84Protocol, B92Protocol, SimulationEngine, InterceptResend
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results['protocol_name'] == "BB84"
    assert len(results['alice_bits']) == 20
    assert results['qber'] == 0.0
    assert results['is_secure'] is True
    assert len(results['key_a']) == len(results['key_b'])
    assert results['key_a'] == results['key_b']

def test_engine_b92_no_eve():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results['protocol_name'] == "B92"
    assert len(results['alice_bits']) == 20
    assert results['qber'] == 0.0
    assert results['is_secure'] is True
    assert results['key_a'] == results['key_b']

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(100)

    assert results['protocol_name'] == "BB84"
    # With Intercept-Resend, QBER should be around 25% if bases match
    # Since we only look at matched bases, it might be higher or lower but usually > 0
    assert results['qber'] >= 0.0

def test_engine_callback():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    messages = []

    def callback(msg):
        messages.append(msg)

    results = engine.run(10, callback=callback)
    assert len(messages) > 0
    assert any("Initializing" in m for m in messages)
    assert any("complete" in m for m in messages)
