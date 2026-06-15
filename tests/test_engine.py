import pytest
from core.engine import SimulationEngine
from core.bb84 import BB84Protocol
from core.b92 import B92Protocol
from qiskit_aer import AerSimulator

def test_engine_bb84_no_eve():
    protocol = BB84Protocol()
    backend = AerSimulator()
    engine = SimulationEngine(protocol, backend)
    n = 20

    results = engine.run(n)

    assert "alice_bits" in results
    assert len(results["alice_bits"]) == n
    assert results["qber"] == 0.0
    assert results["is_secure"] is True
    assert results["protocol_name"] == "BB84"

def test_engine_b92_no_eve():
    protocol = B92Protocol()
    backend = AerSimulator()
    engine = SimulationEngine(protocol, backend)
    n = 20

    results = engine.run(n)

    assert "alice_bits" in results
    assert len(results["alice_bits"]) == n
    assert results["qber"] == 0.0
    assert results["is_secure"] is True
