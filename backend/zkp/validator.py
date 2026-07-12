from dataclasses import dataclass

from backend.zkp.params import SchnorrParams


@dataclass(frozen=True)
class ProofValidationResult:
    """Result of proof shape validation before cryptographic verification."""

    is_valid: bool
    reason: str


class ProofValidator:
    """Validate Schnorr proof values before modular arithmetic."""

    def __init__(self, params: SchnorrParams) -> None:
        """Create a validator for fixed Schnorr parameters."""
        self._params = params

    def validate(self, public_key: int, commitment: int, challenge: int, response: int) -> ProofValidationResult:
        """Check public key, commitment, challenge, and response ranges."""
        if not 1 < public_key < self._params.p:
            return ProofValidationResult(False, "Public key is outside the Schnorr group.")
        if not 1 < commitment < self._params.p:
            return ProofValidationResult(False, "Commitment is outside the Schnorr group.")
        if not 0 <= challenge < self._params.q:
            return ProofValidationResult(False, "Challenge is outside the valid range.")
        if not 0 <= response < self._params.q:
            return ProofValidationResult(False, "Response is outside the valid range.")
        return ProofValidationResult(True, "Proof input is well formed.")
