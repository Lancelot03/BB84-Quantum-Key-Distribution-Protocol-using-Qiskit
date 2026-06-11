import pytest
from core import BB84Protocol, B92Protocol, SimulationEngine, InterceptResend
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert "alice_bits" in results
    assert "key_a" in results
    assert "key_b" in results
    assert len(results["alice_bits"]) == 20
    # Without Eve, keys should match
    assert results["key_a"] == results["key_b"]
    assert results["qber"] == 0.0

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(100)

    assert "qber" in results
    # With Intercept-Resend, QBER should be around 0.25
    # Use a broad range due to randomness
    assert 0.1 < results["qber"] < 0.4

def test_engine_b92_no_eve():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(50)

    assert results["key_a"] == results["key_b"]
    assert results["qber"] == 0.0

def test_engine_callback():
    messages = []
    def callback(msg):
        messages.append(msg)

    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    engine.run(10, callback=callback)

    assert len(messages) > 0
    assert "Generating bits and bases..." in messages
    assert "Analyzing results..." in messages
