import hashlib

class PrivacyAmplifier:
    """
    Implements Privacy Amplification to reduce Eve's potential knowledge.
    Uses hashing to compress the reconciled key into a shorter, more secure key.
    """
    def __init__(self, compression_factor=None):
        """
        compression_factor: Fraction of the key to keep.
        If None, it will be calculated based on QBER or default to 0.8.
        """
        self.compression_factor = compression_factor

    def amplify(self, key: list[int], qber: float = None) -> list[int]:
        """
        Compress the key using a hash function.
        Returns the amplified key as a list of bits.
        """
        if not key:
            return []

        # Convert bit list to string for hashing
        key_str = "".join(map(str, key))

        # Determine output length
        n = len(key)
        if self.compression_factor is not None:
            output_len = int(n * self.compression_factor)
        elif qber is not None:
            # Simple heuristic: lower QBER allows higher rate
            # In practice, this is governed by the Holevo bound and other factors
            factor = max(0.1, 1.0 - 2.0 * qber)
            output_len = int(n * factor)
        else:
            output_len = int(n * 0.8) # Default 20% compression

        output_len = max(1, output_len)

        # Use SHA-256 and truncate/expand as needed
        # (Simplified privacy amplification)
        hash_obj = hashlib.sha256(key_str.encode())
        seed = hash_obj.digest()

        # Generate bit stream from seed to match output_len
        final_key = []
        byte_idx = 0
        while len(final_key) < output_len:
            byte = seed[byte_idx % len(seed)]
            for i in range(8):
                if len(final_key) < output_len:
                    final_key.append((byte >> i) & 1)
                else:
                    break
            byte_idx += 1
            if byte_idx % len(seed) == 0:
                # Re-hash for more entropy if needed
                hash_obj = hashlib.sha256(seed)
                seed = hash_obj.digest()

        return final_key
