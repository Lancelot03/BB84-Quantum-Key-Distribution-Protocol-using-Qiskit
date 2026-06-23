import pytest
from core.engine import SimulationEngine
from core.bb84 import BB84Protocol
from core.b92 import B92Protocol
from core.attacks import InterceptResend
from qiskit_aer import AerSimulator

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
    assert results['key_a'] == results['key_b']
    assert results['qber'] == 0.0
    assert results['is_secure'] is True

def test_engine_b92_no_attack():
    engine = SimulationEngine()
    protocol = B92Protocol()
    n = 20
    results = engine.run(protocol, n)

    assert results['protocol_name'] == "B92"
    assert len(results['alice_bits']) == n
    assert len(results['alice_bases']) == n
    assert all(b == "B92" for b in results['alice_bases'])
    assert results['key_a'] == results['key_b']
    assert results['qber'] == 0.0

def test_engine_with_attack():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    attack = InterceptResend()
    n = 100
    results = engine.run(protocol, n, attack=attack)

    assert results['protocol_name'] == "BB84"
    # QBER should be > 0 with InterceptResend
    assert results['qber'] > 0
    assert results['report'] is not None
    assert 'z_error_rate' in results['report']

def test_engine_callback():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    messages = []
    def callback(msg):
        messages.append(msg)

    engine.run(protocol, 10, callback=callback)
    assert len(messages) > 0
    assert any("Initializing" in m for m in messages)
    assert any("Simulation complete" in m for m in messages)
