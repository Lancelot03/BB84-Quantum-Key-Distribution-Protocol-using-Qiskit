#!/usr/bin/env python3
"""
Phase 1 Verification Script for BB84 Quantum Key Distribution Simulator.
Validates:
1. Alice/Bob Basis Generation
2. Quantum Circuit Generation & Encoding
3. Key Sifting
4. QBER Calculation & Error Analysis
5. Eavesdropper Attack Models (Intercept-Resend, Noisy Channel, PNS)
6. Engine Workflow & Visual Data Output
"""

import sys
from core import (
    BB84Protocol,
    B92Protocol,
    InterceptResend,
    NoisyChannel,
    PhotonNumberSplitting,
    SimulationEngine,
    calculate_qber
)
from visuals import get_bloch_coordinates

def test_phase1():
    print("🚀 Starting Phase 1 BB84 Verification...")

    # 1. BB84 Protocol Basis & Encoding Verification
    bb84 = BB84Protocol()
    bits = bb84.generate_bits(20)
    alice_bases = bb84.generate_alice_bases(20)
    bob_bases = bb84.generate_bases(20)

    assert len(bits) == 20, "Bit length mismatch"
    assert len(alice_bases) == 20, "Alice basis length mismatch"
    assert len(bob_bases) == 20, "Bob basis length mismatch"
    assert set(alice_bases).issubset({'Z', 'X'}), "Invalid Alice bases"
    assert set(bob_bases).issubset({'Z', 'X'}), "Invalid Bob bases"
    print("✅ 1. Alice/Bob Basis Generation verified.")

    # 2. Quantum Circuit Generation Verification
    circuits = bb84.encode(bits, alice_bases)
    assert len(circuits) == 20, "Circuit count mismatch"
    coords = get_bloch_coordinates(circuits[0])
    assert len(coords) == 3, "Bloch coordinates format mismatch"
    print("✅ 2. Quantum Circuit Generation & Bloch sphere vector extraction verified.")

    # 3. Ideal Execution & Sifting Verification (No Eve)
    engine = SimulationEngine()
    res_clean = engine.run(protocol=bb84, n=100)
    assert res_clean['qber'] == 0.0, f"Expected 0% QBER in ideal channel, got {res_clean['qber']}"
    assert res_clean['key_a'] == res_clean['key_b'], "Sifted keys must match perfectly without noise/Eve"
    print(f"✅ 3. Key Sifting & Ideal Simulation verified. Sifted key length: {len(res_clean['key_a'])} bits.")

    # 4. Eve Attack Simulation Verification
    # 4a. Intercept-Resend Attack (100% Intercept) -> expected ~25% QBER
    attack_ir = InterceptResend(intercept_probability=1.0)
    res_ir = engine.run(protocol=bb84, n=200, attack=attack_ir)
    print(f"   Intercept-Resend (100% prob) QBER: {res_ir['qber']*100:.2f}%")
    assert 0.10 <= res_ir['qber'] <= 0.45, "QBER should be significantly elevated under Intercept-Resend"
    assert not res_ir['is_secure'], "Channel should be flagged as compromised"

    # 4b. Noisy Channel Attack
    attack_noise = NoisyChannel(noise_level=0.2)
    res_noise = engine.run(protocol=bb84, n=200, attack=attack_noise)
    print(f"   Noisy Channel (20% noise) QBER: {res_noise['qber']*100:.2f}%")
    assert res_noise['qber'] > 0.0, "Noise should introduce non-zero QBER"

    # 4c. PNS Attack
    attack_pns = PhotonNumberSplitting()
    res_pns = engine.run(protocol=bb84, n=100, attack=attack_pns)
    print(f"   PNS Attack QBER: {res_pns['qber']*100:.2f}%, Eve Info Gain: {res_pns['eve_info_gain']}")
    assert res_pns['eve_info_gain'] == 0.25, "PNS attack info gain should be recorded"

    print("✅ 4. Eavesdropper Simulation Models verified.")

    # 5. Error Analysis Verification
    report = res_ir['report']
    assert 'z_error_rate' in report and 'x_error_rate' in report, "Missing error rate metrics in report"
    assert 'basis_match_efficiency' in report, "Missing sifting efficiency in report"
    print("✅ 5. Error Analysis & Report Generation verified.")

    print("\n🎉 ALL PHASE 1 REQUIREMENTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_phase1()
