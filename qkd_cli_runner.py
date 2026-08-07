#!/usr/bin/env python3
"""
QKD CLI Runner
Command-line interface for running BB84 and B92 Quantum Key Distribution simulations,
eavesdropper attacks, and detailed post-processing (error correction and privacy amplification).
"""

import sys
import argparse
from core import (
    BB84Protocol,
    B92Protocol,
    InterceptResend,
    NoisyChannel,
    PhotonNumberSplitting,
    SimulationEngine
)

def run_simulation(protocol_name, qubits, eve_present, attack_name, noise_level):
    """Run QKD simulation with the given parameters and print a detailed text-based report."""
    # 1. Initialize Protocol
    if protocol_name.upper() == "BB84":
        protocol = BB84Protocol()
    elif protocol_name.upper() == "B92":
        protocol = B92Protocol()
    else:
        print(f"Error: Unknown protocol '{protocol_name}'")
        sys.exit(1)

    # 2. Initialize Attack
    attack = None
    if eve_present:
        if attack_name == "Intercept-Resend":
            attack = InterceptResend(noise_level)
        elif attack_name == "Noisy Channel":
            attack = NoisyChannel(noise_level)
        elif attack_name == "Photon Number Splitting":
            attack = PhotonNumberSplitting()
        else:
            print(f"Error: Unknown attack model '{attack_name}'")
            sys.exit(1)

    print("=" * 60)
    print(f"Starting QKD Simulation: {protocol.name} Protocol")
    print(f"Qubits: {qubits} | Eve Present: {eve_present} " +
          (f"({attack_name}, Strength: {noise_level})" if eve_present else ""))
    print("=" * 60)

    # 3. Setup Simulation Engine
    engine = SimulationEngine()

    # Progress/Status Callback
    def cli_callback(msg, progress=None):
        pct = f" [{int(progress*100)}%]" if progress is not None else ""
        print(f"-> {msg}{pct}")

    viz_data = engine.run(
        protocol=protocol,
        n=qubits,
        attack=attack,
        callback=cli_callback
    )

    # 4. Print Beautiful Text Report
    print("\n" + "=" * 60)
    print("📊 SIMULATION REPORT")
    print("=" * 60)

    # Sifted Keys
    key_a_str = "".join(map(str, viz_data['key_a']))
    key_b_str = "".join(map(str, viz_data['key_b']))
    print(f"Alice's Sifted Key ({len(viz_data['key_a'])} bits): {key_a_str[:60] + ('...' if len(key_a_str) > 60 else '')}")
    print(f"Bob's Sifted Key   ({len(viz_data['key_b'])} bits): {key_b_str[:60] + ('...' if len(key_b_str) > 60 else '')}")
    print(f"QBER (Quantum Bit Error Rate): {viz_data['qber'] * 100:.2f}%")
    print(f"Security Status:               {viz_data['security_status']}")

    if not viz_data['is_secure']:
        print("⚠️  Warning: High QBER detected! Potential eavesdropping or high noise on the channel.")
    else:
        print("✅  Channel is secure. Proceeding with Post-Processing details:")
        report = viz_data.get('report', {})
        if report:
            print(f"   - Sifting Efficiency:     {report.get('basis_match_efficiency', 0.0):.1f}%")
            print(f"   - Z-Basis Error Rate:     {report.get('z_error_rate', 0.0)*100:.1f}%")
            print(f"   - X-Basis Error Rate:     {report.get('x_error_rate', 0.0)*100:.1f}%")
            print(f"   - Information Leakage:    {report.get('info_leakage', 0.0)*100:.1f}%")
            print(f"   - Errors Corrected (Bob): {report.get('errors_fixed', 0)}")
            print(f"   - Final Key Length:       {report.get('final_key_length', 0)} bits")
            print(f"   - Secret Key Rate:        {report.get('secret_key_rate', 0.0)*100:.1f}%")

            # Reconciled and Final Amplified Keys
            reconciled_b_str = "".join(map(str, viz_data['reconciled_key_b']))
            final_a_str = "".join(map(str, viz_data['final_key_a']))
            final_b_str = "".join(map(str, viz_data['final_key_b']))
            print(f"\n   Reconciled Key (Bob):     {reconciled_b_str[:60] + ('...' if len(reconciled_b_str) > 60 else '')}")
            print(f"   Final Amplified Key (A):  {final_a_str[:60] + ('...' if len(final_a_str) > 60 else '')}")
            print(f"   Final Amplified Key (B):  {final_b_str[:60] + ('...' if len(final_b_str) > 60 else '')}")

            if final_a_str == final_b_str:
                print("   🎉 Keys Match! Post-processing completed successfully.")
            else:
                print("   ❌ Key Mismatch! Post-processing failed.")

    print("=" * 60 + "\n")
    return viz_data

def interactive_mode():
    """Run an interactive prompt in the terminal to gather parameters and run the simulation."""
    print("Welcome to the QKD Simulator Interactive CLI!")
    print("-" * 45)

    # Protocol Choice
    protocol_choice = input("Select Protocol (BB84 / B92) [default: BB84]: ").strip()
    if not protocol_choice:
        protocol_choice = "BB84"
    elif protocol_choice.upper() not in ["BB84", "B92"]:
        print(f"Invalid option '{protocol_choice}'. Defaulting to BB84.")
        protocol_choice = "BB84"

    # Number of Qubits
    qubits_str = input("Enter number of qubits (10-200) [default: 100]: ").strip()
    if not qubits_str:
        qubits = 100
    else:
        try:
            qubits = int(qubits_str)
            if qubits < 10 or qubits > 500:
                print("Qubits out of recommended range. Using 100.")
                qubits = 100
        except ValueError:
            print("Invalid input. Defaulting to 100 qubits.")
            qubits = 100

    # Eve Present
    eve_input = input("Simulate Eavesdropper (Eve)? (y/n) [default: n]: ").strip().lower()
    eve_present = (eve_input == 'y' or eve_input == 'yes')

    # Attack selection if Eve present
    attack_choice = "Intercept-Resend"
    noise_level = 0.1
    if eve_present:
        print("\nChoose Eve's Attack Model:")
        print("1. Intercept-Resend")
        print("2. Noisy Channel")
        print("3. Photon Number Splitting")
        attack_opt = input("Select option (1-3) [default: 1]: ").strip()
        if attack_opt == "2":
            attack_choice = "Noisy Channel"
        elif attack_opt == "3":
            attack_choice = "Photon Number Splitting"
        else:
            attack_choice = "Intercept-Resend"

        if attack_choice != "Photon Number Splitting":
            noise_str = input("Enter attack strength / channel noise (0.0 to 0.5) [default: 0.1]: ").strip()
            if noise_str:
                try:
                    noise_level = float(noise_str)
                    if noise_level < 0.0 or noise_level > 0.5:
                        print("Value must be between 0.0 and 0.5. Using 0.1.")
                        noise_level = 0.1
                except ValueError:
                    print("Invalid format. Defaulting to 0.1.")
                    noise_level = 0.1

    run_simulation(protocol_choice, qubits, eve_present, attack_choice, noise_level)

def main():
    parser = argparse.ArgumentParser(description="BB84 / B92 Quantum Key Distribution Simulator CLI")
    parser.add_argument("-p", "--protocol", type=str, choices=["BB84", "B92", "bb84", "b92"], default="BB84",
                        help="QKD protocol to simulate (default: BB84)")
    parser.add_argument("-n", "--qubits", type=int, default=100,
                        help="Number of qubits to transmit (default: 100)")
    parser.add_argument("-e", "--eve", action="store_true",
                        help="Simulate an eavesdropper (Eve) on the channel")
    parser.add_argument("-a", "--attack", type=str,
                        choices=["Intercept-Resend", "Noisy Channel", "Photon Number Splitting"],
                        default="Intercept-Resend",
                        help="Eavesdropper attack model (default: Intercept-Resend)")
    parser.add_argument("-s", "--strength", type=float, default=0.1,
                        help="Attack strength / channel noise level between 0.0 and 0.5 (default: 0.1)")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run the runner in interactive console mode")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    else:
        run_simulation(args.protocol, args.qubits, args.eve, args.attack, args.strength)

if __name__ == "__main__":
    main()
