import hashlib
import secrets
from dataclasses import dataclass

from backend.zkp.params import SchnorrParams


@dataclass(frozen=True)
class SchnorrProof:
    """Schnorr proof values exchanged between prover and verifier."""

    commitment: int
    challenge: int
    response: int


class SchnorrProtocol:
    """Implement Schnorr proof generation and verification over Z_p."""

    def __init__(self, params: SchnorrParams) -> None:
        """Create a protocol instance with fixed group parameters."""
        self._params = params

    def public_key_from_secret(self, secret_key: int) -> int:
        """Derive y = g^x mod p from a secret key."""
        return pow(self._params.g, secret_key % self._params.q, self._params.p)

    def create_interactive_response(
        self,
        secret_key: int,
        nonce: int,
        challenge: int,
    ) -> int:
        """Create s = r + c*x mod q for an interactive Schnorr challenge."""
        # Schnorr identification:
        # public key y = g^x mod p, commitment t = g^r mod p.
        # Given challenge c, prover returns s = r + c*x mod q.
        return (nonce + challenge * secret_key) % self._params.q

    def create_non_interactive_proof(self, secret_key: int, message: str) -> SchnorrProof:
        """Create a Fiat-Shamir Schnorr proof bound to a message."""
        nonce = secrets.randbelow(self._params.q - 1) + 1
        commitment = pow(self._params.g, nonce, self._params.p)
        challenge = self.derive_challenge(commitment, message)
        response = self.create_interactive_response(secret_key, nonce, challenge)
        return SchnorrProof(commitment=commitment, challenge=challenge, response=response)

    def derive_challenge(self, commitment: int, message: str) -> int:
        """Derive a deterministic challenge from commitment and message."""
        digest = hashlib.sha256(f"{commitment}:{message}".encode("utf-8")).digest()
        return int.from_bytes(digest, "big") % self._params.q

    def verify(
        self,
        public_key: int,
        commitment: int,
        challenge: int,
        response: int,
    ) -> bool:
        """Verify g^s == t * y^c mod p."""
        if not self._is_valid_public_value(public_key) or not self._is_valid_public_value(commitment):
            return False
        if not 0 <= challenge < self._params.q or not 0 <= response < self._params.q:
            return False

        # Verification checks g^s == t * y^c mod p.
        # With s = r + c*x, right side becomes g^r * (g^x)^c = g^(r + c*x).
        left = pow(self._params.g, response, self._params.p)
        right = (commitment * pow(public_key, challenge, self._params.p)) % self._params.p
        return left == right

    def _is_valid_public_value(self, value: int) -> bool:
        """Return true when a value is a plausible group element."""
        return 1 < value < self._params.p
