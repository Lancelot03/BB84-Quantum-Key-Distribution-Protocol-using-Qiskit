#!/usr/bin/env python3
"""
QKD CLI Runner - Command-line interface for running BB84 and B92 Quantum Key Distribution simulations.
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

def run_simulation(protocol_name, n_qubits, attack_name, noise_level):
    # Initialize Protocol
    if protocol_name.upper() == "BB84":
        protocol = BB84Protocol()
    elif protocol_name.upper() == "B92":
        protocol = B92Protocol()
    else:
        print(f"Error: Unknown protocol '{protocol_name}'", file=sys.stderr)
        return 1

    # Initialize Attack
    attack = None
    if attack_name:
        if attack_name == "Intercept-Resend":
            attack = InterceptResend(noise_level)
        elif attack_name == "Noisy-Channel":
            attack = NoisyChannel(noise_level)
        elif attack_name == "PNS":
            attack = PhotonNumberSplitting()
        else:
            print(f"Error: Unknown attack model '{attack_name}'", file=sys.stderr)
            return 1

    engine = SimulationEngine()

    print("=" * 60)
    print(f"Starting {protocol.name} QKD Simulation")
    print(f"Qubits: {n_qubits} | Attack: {attack_name or 'None'} | Noise/Strength: {noise_level}")
    print("=" * 60)

    # We do a simple callback to show progress in command line
    def cli_callback(msg, progress=None):
        prog_str = f" [{int(progress * 100)}%]" if progress is not None else ""
        print(f"[*] {msg}{prog_str}")

    results = engine.run(
        protocol=protocol,
        n=n_qubits,
        attack=attack,
        callback=cli_callback
    )

    print("\n" + "=" * 60)
    print("                      SIMULATION REPORT                      ")
    print("=" * 60)
    print(f"Protocol:               {results['protocol_name']}")
    print(f"Total Qubits:           {n_qubits}")
    print(f"Sifted Key Length:      {len(results['key_a'])}")
    print(f"Initial QBER:           {results['qber'] * 100:.2f}%")
    print(f"Security Status:        {results['security_status']}")

    if results['report']:
        report = results['report']
        print(f"Sifting Efficiency:     {report.get('basis_match_efficiency', 0.0):.1f}%")
        print(f"Z-Basis Error Rate:     {report.get('z_error_rate', 0.0) * 100:.1f}%")
        print(f"X-Basis Error Rate:     {report.get('x_error_rate', 0.0) * 100:.1f}%")
        print(f"Information Leakage:    {report.get('info_leakage', 0.0) * 100:.1f}%")

        if results['is_secure']:
            print("-" * 60)
            print("Post-Processing Results:")
            print(f"  Errors Corrected:     {report.get('errors_fixed', 0)}")
            print(f"  Final Key Length:     {report.get('final_key_length', 0)} bits")
            print(f"  Secret Key Rate:      {report.get('secret_key_rate', 0.0) * 100:.1f}%")

            # Print a snippet of final keys
            key_a_str = "".join(map(str, results['final_key_a']))
            key_b_str = "".join(map(str, results['final_key_b']))
            snippet_len = min(40, len(key_a_str))
            suffix = "..." if len(key_a_str) > snippet_len else ""
            print(f"  Alice's Final Key:    {key_a_str[:snippet_len]}{suffix}")
            print(f"  Bob's Final Key:      {key_b_str[:snippet_len]}{suffix}")

            if results['final_key_a'] == results['final_key_b']:
                print("  [✓] Final keys matched perfectly!")
            else:
                print("  [✗] Final key mismatch!")

    print("=" * 60)
    return 0

def main():
    parser = argparse.ArgumentParser(description="QKD Protocol CLI Simulation Runner")
    parser.add_argument("--protocol", type=str, choices=["BB84", "B92", "bb84", "b92"], default="BB84",
                        help="QKD protocol to run (default: BB84)")
    parser.add_argument("--qubits", type=int, default=100,
                        help="Number of qubits to transmit (default: 100)")
    parser.add_argument("--attack", type=str, choices=["Intercept-Resend", "Noisy-Channel", "PNS"], default=None,
                        help="Eavesdropper/Channel Attack model (default: None)")
    parser.add_argument("--noise", type=float, default=0.1,
                        help="Channel noise level or attack strength between 0.0 and 0.5 (default: 0.1)")

    args = parser.parse_args()

    # Validate noise
    if args.noise < 0.0 or args.noise > 0.5:
        print("Error: Noise level must be between 0.0 and 0.5", file=sys.stderr)
        sys.exit(1)

    sys.exit(run_simulation(args.protocol, args.qubits, args.attack, args.noise))

if __name__ == "__main__":
    main()
