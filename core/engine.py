from typing import List, Dict, Any, Optional, Callable
from core.protocol import QKDProtocol
from core.stats import calculate_qber, analyze_security, generate_error_report, calculate_info_leakage
from core.reconciliation import CascadeReconciler
from core.privacy import PrivacyAmplifier

class SimulationEngine:
    """
    Orchestrates the QKD simulation flow, decoupling the protocol logic from the UI.
    """
    def run(
        self,
        protocol: QKDProtocol,
        n: int,
        attack: Optional[Any] = None,
        backend: Optional[Any] = None,
        callback: Optional[Callable[[str, Optional[float]], None]] = None
    ) -> Dict[str, Any]:
        """
        Run a full QKD simulation.

        Args:
            protocol: The QKD protocol instance (e.g., BB84Protocol).
            n: Number of qubits to simulate.
            attack: Optional attack model instance.
            backend: Optional Qiskit backend.
            callback: Optional UI callback for status and progress updates.

        Returns:
            A dictionary containing simulation results and metadata.
        """
        def log(msg: str, progress: Optional[float] = None) -> None:
            if callback:
                import inspect
                try:
                    sig = inspect.signature(callback)
                    if len(sig.parameters) >= 2:
                        callback(msg, progress)
                    else:
                        callback(msg)
                except Exception:
                    try:
                        callback(msg)
                    except Exception:
                        pass

        log(f"Initializing {protocol.name} simulation with {n} qubits...", 0.1)

        # Alice's side: bit and basis generation
        alice_bits = protocol.generate_bits(n)
        alice_bases = protocol.generate_alice_bases(n)

        # Encoding into quantum circuits
        circuits = protocol.encode(alice_bits, alice_bases)
        log("Quantum states encoded.", 0.3)

        # Optional Eavesdropper/Channel Attack
        eve_info_gain = 0.0
        if attack:
            log(f"Applying {type(attack).__name__} attack to the channel...", 0.4)
            intercepted_circuits, intercepted_info = attack.apply(circuits, backend)
            eve_info_gain = intercepted_info.get('info_gain', 0.0)
        else:
            intercepted_circuits = circuits

        # Bob's side: basis generation and measurement
        bob_bases = protocol.generate_bases(n)
        log("Bob is measuring the received qubits...", 0.6)
        bob_results, meas_circuits = protocol.measure(intercepted_circuits, bob_bases, backend)

        # Sifting process (reconciling keys over classical channel)
        log("Performing key sifting...", 0.8)
        key_a, key_b, indices = protocol.sift(alice_bases, bob_bases, alice_bits, bob_results)

        # Error analysis and security verification
        log("Analyzing Quantum Bit Error Rate (QBER)...", 0.85)
        qber = calculate_qber(key_a, key_b)
        is_secure, security_status = analyze_security(qber)

        # Phase 2: Post-Processing
        reconciled_key_b = key_b
        errors_fixed = 0
        final_key_a = key_a
        final_key_b = reconciled_key_b

        if is_secure:
            log("Starting Information Reconciliation...", 0.9)
            reconciler = CascadeReconciler()
            reconciled_key_b, errors_fixed = reconciler.reconcile(key_a, key_b)

            log("Starting Privacy Amplification...", 0.95)
            amplifier = PrivacyAmplifier()
            final_key_a = amplifier.amplify(key_a, qber)
            final_key_b = amplifier.amplify(reconciled_key_b, qber)

        leakage = calculate_info_leakage(qber, eve_info_gain)

        report = generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, key_a, key_b, qber, protocol.name)
        report['info_leakage'] = leakage
        if is_secure:
            report['errors_fixed'] = errors_fixed
            report['final_key_length'] = len(final_key_a)
            report['secret_key_rate'] = len(final_key_a) / n if n > 0 else 0

        log("Simulation complete.", 1.0)
        return {
            "protocol_name": protocol.name,
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_results": bob_results,
            "key_a": key_a,
            "key_b": key_b,
            "reconciled_key_b": reconciled_key_b,
            "final_key_a": final_key_a,
            "final_key_b": final_key_b,
            "indices": indices,
            "qber": qber,
            "is_secure": is_secure,
            "security_status": security_status,
            "report": report,
            "alice_circuits": circuits,
            "bob_circuits": meas_circuits,
            "received_circuits": intercepted_circuits,
            "eve_info_gain": eve_info_gain
        }
