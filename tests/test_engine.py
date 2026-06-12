import pytest
from core.bb84 import BB84Protocol
from core.engine import SimulationEngine
from core.attacks import InterceptResend

def test_simulation_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(n=20)

    assert "alice_bits" in results
    assert "key_a" in results
    assert "key_b" in results
    assert results["qber"] == 0.0
    assert results["is_secure"] == True

def test_simulation_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(n=100)

    assert "alice_bits" in results
    # With Intercept-Resend, QBER should be > 0 (typically ~25%)
    assert results["qber"] > 0
    assert "report" in results
    assert "eve_info_gain" in results["report"]

def test_simulation_engine_callback():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    messages = []
    def callback(msg):
        messages.append(msg)

    engine.run(n=10, callback=callback)
    assert len(messages) > 0
    assert any("Generating" in m for m in messages)
    assert any("Simulation complete!" in m for m in messages)
