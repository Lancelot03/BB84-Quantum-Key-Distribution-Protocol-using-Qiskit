import pytest
from core.bb84 import BB84Protocol
from core.engine import SimulationEngine
from core.attacks import InterceptResend
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(n=20)

    assert results['protocol_name'] == "BB84"
    assert len(results['alice_bits']) == 20
    assert results['qber'] == 0.0
    assert results['is_secure'] is True
    assert len(results['key_a']) == len(results['key_b'])
    assert results['key_a'] == results['key_b']

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack=attack)
    results = engine.run(n=100)

    assert results['protocol_name'] == "BB84"
    # QBER should be around 0.25 for Intercept-Resend on BB84
    assert results['qber'] > 0.1
    assert results['security_status'] in ["Secure", "Compromised"]

def test_engine_callback():
    protocol = BB84Protocol()
    messages = []
    def callback(msg):
        messages.append(msg)

    engine = SimulationEngine(protocol)
    engine.run(n=10, callback=callback)

    assert len(messages) > 0
    assert any("Alice: Generating random bits..." in m for m in messages)
    assert any("Simulation complete." in m for m in messages)
