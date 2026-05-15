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
