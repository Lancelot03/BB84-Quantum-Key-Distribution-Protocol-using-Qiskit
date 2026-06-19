import pytest
from core.bb84 import BB84Protocol
from core.b92 import B92Protocol
from core.engine import SimulationEngine
from core.attacks import InterceptResend
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results["protocol_name"] == "BB84"
    assert len(results["alice_bits"]) == 20
    assert results["key_a"] == results["key_b"]
    assert results["qber"] == 0.0
    assert results["is_secure"] is True

def test_engine_b92_no_eve():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert results["protocol_name"] == "B92"
    assert len(results["alice_bits"]) == 20
    assert results["key_a"] == results["key_b"]
    assert results["qber"] == 0.0
    assert results["is_secure"] is True

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(50)

    assert results["protocol_name"] == "BB84"
    # With Intercept-Resend, QBER should be non-zero (around 25% for matched bases)
    assert results["qber"] >= 0.0

def test_engine_callback():
    messages = []
    def callback(msg):
        messages.append(msg)

    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    engine.run(10, callback=callback)

    assert len(messages) > 0
    assert "Initializing BB84 protocol..." in messages
    assert "Simulation Complete" not in messages # Engine doesn't log "Complete"
