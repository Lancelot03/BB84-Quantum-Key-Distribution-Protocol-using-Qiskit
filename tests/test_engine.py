import pytest
from core import SimulationEngine, BB84Protocol, B92Protocol, InterceptResend

def test_engine_run_bb84():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    results = engine.run(protocol, n=20)

    assert results['protocol_name'] == "BB84"
    assert len(results['alice_bits']) == 20
    assert len(results['key_a']) == len(results['key_b'])
    assert results['qber'] == 0.0 # No eve, no noise

def test_engine_run_b92():
    engine = SimulationEngine()
    protocol = B92Protocol()
    results = engine.run(protocol, n=20)

    assert results['protocol_name'] == "B92"
    assert len(results['alice_bits']) == 20
    assert len(results['key_a']) == len(results['key_b'])
    assert results['qber'] == 0.0

def test_engine_with_eve():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    attack = InterceptResend()
    results = engine.run(protocol, n=100, eve_present=True, attack=attack)

    assert results['qber'] > 0 # Eve should introduce errors
