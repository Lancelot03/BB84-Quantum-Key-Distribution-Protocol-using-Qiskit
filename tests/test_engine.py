import pytest
from core.bb84 import BB84Protocol
from core.b92 import B92Protocol
from core.engine import SimulationEngine
from core.attacks import InterceptResend

def test_engine_run_bb84():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results['protocol_name'] == "BB84"
    assert len(results['alice_bits']) == 20
    assert len(results['key_a']) == len(results['key_b'])
    assert results['qber'] == 0.0 # No Eve, BB84 should be perfect

def test_engine_run_b92():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(50)

    assert results['protocol_name'] == "B92"
    assert len(results['alice_bits']) == 50
    assert len(results['key_a']) == len(results['key_b'])
    assert results['qber'] == 0.0

def test_engine_with_attack():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(100)

    assert results['qber'] > 0 # Eve should introduce errors

def test_engine_callback():
    protocol = BB84Protocol()
    messages = []
    def callback(msg):
        messages.append(msg)

    engine = SimulationEngine(protocol)
    engine.run(10, callback=callback)

    assert len(messages) > 0
    assert "Simulation complete." in messages
