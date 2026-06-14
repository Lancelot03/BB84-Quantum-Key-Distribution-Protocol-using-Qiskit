import pytest
from core import SimulationEngine, BB84Protocol, B92Protocol, InterceptResend
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert "key_a" in results
    assert "key_b" in results
    assert results["key_a"] == results["key_b"]
    assert results["qber"] == 0.0
    assert results["is_secure"] is True

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(100)

    assert "qber" in results
    # Intercept-Resend introduces error
    assert results["qber"] > 0
    assert "report" in results
    assert "eve_info_gain" in results["report"]

def test_engine_b92():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(50)

    assert "key_a" in results
    assert len(results["key_a"]) <= 50
    assert results["key_a"] == results["key_b"]
    assert results["alice_bases"] == ['B92'] * 50

def test_engine_callback():
    messages = []
    def callback(msg):
        messages.append(msg)

    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    engine.run(10, callback=callback)

    assert len(messages) > 0
    assert "Simulation complete!" in messages
