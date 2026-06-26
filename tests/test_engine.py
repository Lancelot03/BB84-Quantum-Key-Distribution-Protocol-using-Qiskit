import pytest
from core import SimulationEngine, BB84Protocol, B92Protocol, InterceptResend
from qiskit_aer import AerSimulator

def test_engine_bb84_no_attack():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results['protocol_name'] == "BB84"
    assert len(results['alice_bits']) == 20
    assert results['qber'] == 0.0
    assert results['is_secure'] is True
    assert len(results['key_a']) == len(results['key_b'])
    assert results['key_a'] == results['key_b']

def test_engine_b92_no_attack():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results['protocol_name'] == "B92"
    assert len(results['alice_bits']) == 20
    assert results['qber'] == 0.0
    assert results['is_secure'] is True
    assert len(results['key_a']) > 0
    assert results['key_a'] == results['key_b']

def test_engine_bb84_with_attack():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(100)

    assert results['protocol_name'] == "BB84"
    # Intercept-Resend should introduce QBER
    assert results['qber'] > 0

def test_engine_callback():
    messages = []
    def callback(msg):
        messages.append(msg)

    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    engine.run(10, callback=callback)

    assert len(messages) > 0
    assert any("Alice" in msg for msg in messages)
    assert any("Bob" in msg for msg in messages)
    assert any("Simulation complete" in msg for msg in messages)
