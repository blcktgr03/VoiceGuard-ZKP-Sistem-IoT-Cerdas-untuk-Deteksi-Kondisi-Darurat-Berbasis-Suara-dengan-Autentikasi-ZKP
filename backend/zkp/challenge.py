import secrets

from backend.zkp.params import SchnorrParams


class ChallengeGenerator:
    """Generate random Schnorr challenges in the valid range."""

    def __init__(self, params: SchnorrParams) -> None:
        """Create a generator for a given Schnorr group."""
        self._params = params

    def generate(self) -> int:
        """Return a random challenge c where 1 <= c < q."""
        return secrets.randbelow(self._params.q - 1) + 1
