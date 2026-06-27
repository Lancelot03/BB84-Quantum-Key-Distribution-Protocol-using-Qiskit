import pytest
from core.bb84 import BB84Protocol
from core.b92 import B92Protocol
from core.attacks import InterceptResend
from core.engine import SimulationEngine
from qiskit_aer import AerSimulator

def test_engine_bb84_no_attack():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    n = 20
    results = engine.run(protocol, n)

    assert results["protocol_name"] == "BB84"
    assert len(results["alice_bits"]) == n
    assert results["qber"] == 0
    assert results["is_secure"] is True
    assert results["key_a"] == results["key_b"]

def test_engine_b92_no_attack():
    engine = SimulationEngine()
    protocol = B92Protocol()
    n = 50
    results = engine.run(protocol, n)

    assert results["protocol_name"] == "B92"
    assert results["qber"] == 0
    assert results["is_secure"] is True
    assert results["key_a"] == results["key_b"]
    assert len(results["key_a"]) > 0

def test_engine_bb84_with_attack():
    engine = SimulationEngine()
    protocol = BB84Protocol()
    attack = InterceptResend()
    n = 100
    results = engine.run(protocol, n, attack=attack)

    assert results["protocol_name"] == "BB84"
    # QBER should be > 0 with Intercept-Resend (around 25%)
    assert results["qber"] > 0
    if results["qber"] > 0.11:
        assert results["is_secure"] is False

def test_engine_callback():
    messages = []
    def callback(msg):
        messages.append(msg)

    engine = SimulationEngine()
    protocol = BB84Protocol()
    engine.run(protocol, 10, callback=callback)

    assert len(messages) > 0
    assert "Simulation complete." in messages
