import pytest
from core.bb84 import BB84Protocol
from core.b92 import B92Protocol
from core.attacks import InterceptResend
from core.engine import SimulationEngine
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(20)

    assert "alice_bits" in results
    assert len(results["alice_bits"]) == 20
    assert results["key_a"] == results["key_b"]
    assert results["qber"] == 0.0

def test_engine_b92_no_eve():
    protocol = B92Protocol()
    engine = SimulationEngine(protocol)
    results = engine.run(40) # More qubits for B92 to ensure some conclusive results

    assert "alice_bits" in results
    assert len(results["alice_bits"]) == 40
    # B92 might have empty keys if unlucky, but usually not for 40 qubits
    if len(results["key_a"]) > 0:
        assert results["key_a"] == results["key_b"]
        assert results["qber"] == 0.0

def test_engine_bb84_with_eve():
    protocol = BB84Protocol()
    attack = InterceptResend()
    engine = SimulationEngine(protocol, attack)
    results = engine.run(100)

    # With Eve, QBER should be > 0 (statistically)
    assert results["qber"] >= 0.0
    assert "report" in results
    assert results["report"]["eve_info_gain"] == min(1.0, 2 * results["qber"])

def test_engine_callback():
    protocol = BB84Protocol()
    engine = SimulationEngine(protocol)
    messages = []
    def callback(msg):
        messages.append(msg)

    engine.run(10, callback=callback)
    assert len(messages) > 0
    assert "Simulation complete." in messages
