def calculate_qber(alice_key, bob_key):
    """Calculate the Quantum Bit Error Rate (QBER)."""
    if not alice_key or len(alice_key) != len(bob_key):
        return 0.0
    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    return errors / len(alice_key)

def analyze_security(qber, threshold=0.11):
    """Determine if the communication is secure based on QBER."""
    is_secure = qber <= threshold
    return is_secure, "Secure" if is_secure else "Compromised"

def generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, sifted_alice, sifted_bob):
    """
    Generate a detailed error analysis report.
    Works for both BB84 and B92.
    """
    total_qubits = len(alice_bits)
    sifted_length = len(sifted_alice)

    # Efficiency of sifting
    basis_match_efficiency = (sifted_length / total_qubits) * 100 if total_qubits > 0 else 0

    # QBER
    qber = calculate_qber(sifted_alice, sifted_bob)

    # Analyze errors per basis (relevant for BB84)
    z_errors = 0
    z_total = 0
    x_errors = 0
    x_total = 0

    is_bb84 = any(b != "B92" for b in alice_bases)

    if is_bb84:
        for i in range(total_qubits):
            if alice_bases[i] == bob_bases[i]:
                if alice_bases[i] == 'Z':
                    z_total += 1
                    if alice_bits[i] != bob_results[i]:
                        z_errors += 1
                elif alice_bases[i] == 'X':
                    x_total += 1
                    if alice_bits[i] != bob_results[i]:
                        x_errors += 1

    z_error_rate = (z_errors / z_total) if z_total > 0 else 0
    x_error_rate = (x_errors / x_total) if x_total > 0 else 0

    return {
        "total_qubits": total_qubits,
        "sifted_length": sifted_length,
        "basis_match_efficiency": basis_match_efficiency,
        "qber": qber,
        "z_error_rate": z_error_rate,
        "x_error_rate": x_error_rate,
        "z_total": z_total,
        "x_total": x_total,
        "protocol": "BB84" if is_bb84 else "B92"
    }
