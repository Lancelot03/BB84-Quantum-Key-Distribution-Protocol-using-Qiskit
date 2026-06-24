import pytest
from core import BB84Protocol, B92Protocol, InterceptResend, SimulationEngine
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results['protocol_name'] == "BB84"
    assert results['key_a'] == results['key_b']
    assert results['qber'] == 0.0
    assert results['is_secure'] is True

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(100)

    assert results['protocol_name'] == "BB84"
    # QBER should be around 25% for BB84 with InterceptResend
    assert 0.1 < results['qber'] < 0.4
    assert results['is_secure'] is False

def test_engine_b92_no_eve():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(100)

    assert results['protocol_name'] == "B92"
    assert results['key_a'] == results['key_b']
    assert results['qber'] == 0.0
    assert len(results['key_a']) > 0
