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

def generate_error_report(alice_bits, bob_results, alice_bases, bob_bases, qber):
    """
    Generate a detailed error analysis report.
    Supports both BB84 and B92 logic.
    """
    total_qubits = len(alice_bits)

    # Analyze errors per basis
    z_errors = 0
    z_total = 0
    x_errors = 0
    x_total = 0

    # Check if we are in B92 mode (Alice bases are usually labeled 'B92' in the current app.py)
    is_b92 = all(b == 'B92' for b in alice_bases)

    for i in range(total_qubits):
        if is_b92:
            # B92 Logic: Sifted only if bob_results[i] == 1
            if bob_results[i] == 1:
                # If Bob measured 1 in Z, Alice must have sent bit 1
                # If Bob measured 1 in X, Alice must have sent bit 0
                if bob_bases[i] == 'Z':
                    z_total += 1
                    if alice_bits[i] != 1:
                        z_errors += 1
                elif bob_bases[i] == 'X':
                    x_total += 1
                    if alice_bits[i] != 0:
                        x_errors += 1
        else:
            # BB84 Logic
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

    sifted_length = z_total + x_total
    basis_match_efficiency = (sifted_length / total_qubits) * 100 if total_qubits > 0 else 0

    return {
        "total_qubits": total_qubits,
        "sifted_length": sifted_length,
        "basis_match_efficiency": basis_match_efficiency,
        "qber": qber,
        "z_error_rate": z_error_rate,
        "x_error_rate": x_error_rate,
        "z_total": z_total,
        "x_total": x_total
    }
