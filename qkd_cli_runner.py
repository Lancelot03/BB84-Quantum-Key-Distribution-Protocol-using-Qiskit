#!/usr/bin/env python3
import argparse
import sys
from core import (
    BB84Protocol,
    B92Protocol,
    InterceptResend,
    NoisyChannel,
    PhotonNumberSplitting,
    SimulationEngine
)

def parse_args(args=None):
    parser = argparse.ArgumentParser(description="QKD (Quantum Key Distribution) CLI Simulator")
    parser.add_argument(
        "--protocol", "-p",
        choices=["BB84", "B92"],
        default="BB84",
        help="QKD Protocol to simulate (default: BB84)"
    )
    parser.add_argument(
        "--qubits", "-n",
        type=int,
        default=100,
        help="Number of qubits to simulate (default: 100)"
    )
    parser.add_argument(
        "--eve", "-e",
        action="store_true",
        help="Simulate an eavesdropper (Eve) on the quantum channel"
    )
    parser.add_argument(
        "--attack", "-a",
        choices=["Intercept-Resend", "Noisy Channel", "Photon Number Splitting"],
        default="Intercept-Resend",
        help="Eavesdropping attack model (default: Intercept-Resend)"
    )
    parser.add_argument(
        "--noise", "-s",
        type=float,
        default=0.1,
        help="Attack strength / channel noise level between 0.0 and 0.5 (default: 0.1)"
    )
    return parser.parse_args(args)

def main():
    args = parse_args()

    # Initialize protocol
    if args.protocol == "BB84":
        protocol = BB84Protocol()
    else:
        protocol = B92Protocol()

    # Initialize attack model
    attack = None
    if args.eve:
        if args.attack == "Intercept-Resend":
            attack = InterceptResend(args.noise)
        elif args.attack == "Noisy Channel":
            attack = NoisyChannel(args.noise)
        elif args.attack == "Photon Number Splitting":
            attack = PhotonNumberSplitting()

    engine = SimulationEngine()

    print("=" * 60)
    print("      🚀 Starting Quantum Key Distribution Simulation 🚀      ")
    print("=" * 60)
    print(f"Protocol:   {args.protocol}")
    print(f"Qubits:     {args.qubits}")
    if args.eve:
        print(f"Eavesdropper: Yes ({args.attack}, strength={args.noise if args.attack != 'Photon Number Splitting' else 'N/A'})")
    else:
        print("Eavesdropper: None")
    print("-" * 60)

    # Callback to show progress on CLI
    def cli_callback(msg, progress=None):
        if progress is not None:
            sys.stdout.write(f"\r[{progress*100:3.0f}%] {msg:<50}")
            sys.stdout.flush()
            if progress >= 1.0:
                print()
        else:
            print(f"[INFO] {msg}")

    viz_data = engine.run(
        protocol=protocol,
        n=args.qubits,
        attack=attack,
        callback=cli_callback
    )

    print("-" * 60)
    print("                       📬 Simulation Results                  ")
    print("-" * 60)

    # Show subset of Alice/Bob keys
    key_length = len(viz_data['key_a'])
    preview_len = min(20, key_length)

    alice_key_str = "".join(map(str, viz_data['key_a']))
    bob_key_str = "".join(map(str, viz_data['key_b']))

    if key_length > preview_len:
        alice_preview = alice_key_str[:preview_len] + "..."
        bob_preview = bob_key_str[:preview_len] + "..."
    else:
        alice_preview = alice_key_str
        bob_preview = bob_key_str

    print(f"Sifted Key Length:  {key_length} bits")
    print(f"Alice's Sifted Key: {alice_preview}")
    print(f"Bob's Sifted Key:   {bob_preview}")
    print(f"QBER:               {viz_data['qber'] * 100:.2f}%")
    print(f"Security Status:    {viz_data['security_status']}")

    # Security conclusions
    if viz_data['is_secure']:
        print("\n[SUCCESS] Low QBER. The transmission is considered secure.")
        print("-" * 60)
        print("               🔐 Post-Processing Details              ")
        print("-" * 60)

        # Reconciliation and Privacy Amplification details
        reconciled_b_str = "".join(map(str, viz_data['reconciled_key_b']))
        if key_length > preview_len:
            reconciled_preview = reconciled_b_str[:preview_len] + "..."
        else:
            reconciled_preview = reconciled_b_str

        print(f"Errors Corrected:             {viz_data['report'].get('errors_fixed', 0)} bits")
        print(f"Bob's Reconciled Key:        {reconciled_preview}")

        # Privacy amplification keys
        final_a_str = "".join(map(str, viz_data['final_key_a']))
        final_b_str = "".join(map(str, viz_data['final_key_b']))
        final_len = len(final_a_str)
        final_preview_len = min(20, final_len)

        if final_len > final_preview_len:
            final_a_prev = final_a_str[:final_preview_len] + "..."
            final_b_prev = final_b_str[:final_preview_len] + "..."
        else:
            final_a_prev = final_a_str
            final_b_prev = final_b_str

        print(f"Final Amplified Key Length:   {final_len} bits")
        print(f"Alice's Final Key:            {final_a_prev}")
        print(f"Bob's Final Key:              {final_b_prev}")

        if final_a_str == final_b_str:
            print("Key Agreement:                Match ✅")
        else:
            print("Key Agreement:                Mismatch ❌")

    else:
        print("\n[WARNING] High QBER detected! The channel is compromised.")
        print("Discarding keys due to potential eavesdropping.")

    print("-" * 60)
    print("                     📊 Detailed Analysis                      ")
    print("-" * 60)
    report = viz_data['report']
    if report:
        print(f"Basis Match Efficiency:  {report['basis_match_efficiency']:.2f}%")
        print(f"Z-Basis Error Rate:      {report['z_error_rate']*100:.2f}% (Total: {report['z_total']})")
        print(f"X-Basis Error Rate:      {report['x_error_rate']*100:.2f}% (Total: {report['x_total']})")
        print(f"Information Leakage:     {report.get('info_leakage', 0.0)*100:.2f}%")
        if viz_data['is_secure']:
            print(f"Secret Key Rate:         {report.get('secret_key_rate', 0.0)*100:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
