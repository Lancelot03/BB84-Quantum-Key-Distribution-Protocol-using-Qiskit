import random

class CascadeReconciler:
    """
    A simplified implementation of the Cascade Error Correction protocol.
    Alice and Bob divide their keys into blocks and compare parities to find and fix errors.
    """
    def __init__(self, block_size=None):
        self.block_size = block_size

    def reconcile(self, alice_key: list[int], bob_key: list[int]) -> tuple[list[int], int]:
        """
        Attempt to reconcile bob_key to match alice_key using parity checks.
        Returns (corrected_bob_key, num_errors_fixed).
        """
        if not alice_key or not bob_key:
            return list(bob_key), 0

        # Work on copies
        a_key = list(alice_key)
        b_key = list(bob_key)
        n = len(a_key)

        # Heuristic for block size if not provided: ~ 0.73 / QBER
        # But since we don't always have QBER, we'll use a default or dynamic one
        if self.block_size is None:
            errors = sum(1 for a, b in zip(a_key, b_key) if a != b)
            qber = errors / n if n > 0 else 0
            block_size = max(2, int(0.73 / qber)) if qber > 0 else n
        else:
            block_size = self.block_size

        errors_fixed = 0

        # Simple one-pass block parity correction (simplified Cascade)
        for i in range(0, n, block_size):
            end = min(i + block_size, n)
            block_a = a_key[i:end]
            block_b = b_key[i:end]

            if self._calculate_parity(block_a) != self._calculate_parity(block_b):
                # Error detected in this block, find it using binary search
                error_idx = self._find_error(a_key[i:end], b_key[i:end])
                if error_idx != -1:
                    actual_idx = i + error_idx
                    # Bob flips his bit to match Alice's
                    b_key[actual_idx] = 1 - b_key[actual_idx]
                    errors_fixed += 1

        return b_key, errors_fixed

    def _calculate_parity(self, bits):
        return sum(bits) % 2

    def _find_error(self, block_a, block_b):
        """Binary search to find a single error in a block with mismatched parity."""
        if len(block_a) == 1:
            return 0

        mid = len(block_a) // 2

        # Check left half
        if self._calculate_parity(block_a[:mid]) != self._calculate_parity(block_b[:mid]):
            return self._find_error(block_a[:mid], block_b[:mid])
        else:
            # Error must be in right half
            res = self._find_error(block_a[mid:], block_b[mid:])
            return mid + res if res != -1 else -1
