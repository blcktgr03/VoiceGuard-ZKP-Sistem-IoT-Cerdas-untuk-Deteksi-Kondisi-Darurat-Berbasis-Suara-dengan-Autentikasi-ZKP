from backend.zkp.challenge import ChallengeGenerator
from backend.zkp.params import DEMO_PARAMS, SchnorrParams
from backend.zkp.schnorr import SchnorrProof, SchnorrProtocol
from backend.zkp.validator import ProofValidator


class ZkpService:
    """Application-facing facade for Schnorr challenge and proof operations."""

    def __init__(self, params: SchnorrParams = DEMO_PARAMS) -> None:
        """Create a ZKP service using configured Schnorr parameters."""
        self._params = params
        self._protocol = SchnorrProtocol(params)
        self._challenge_generator = ChallengeGenerator(params)
        self._validator = ProofValidator(params)

    @property
    def params(self) -> SchnorrParams:
        """Return the active Schnorr parameters."""
        return self._params

    def generate_challenge(self) -> int:
        """Generate a random interactive challenge."""
        return self._challenge_generator.generate()

    def get_public_key(self, secret_key: int) -> int:
        """Derive the public key for a secret key."""
        return self._protocol.public_key_from_secret(secret_key)

    def create_server_proof(self, secret_key: int, message: str) -> SchnorrProof:
        """Create the server proof included in classification responses."""
        return self._protocol.create_non_interactive_proof(secret_key, message)

    def verify(
        self,
        public_key: str,
        commitment: str,
        challenge: int | str,
        response: str,
    ) -> bool:
        """Validate and verify a device Schnorr proof."""
        try:
            public_key_int = int(public_key)
            commitment_int = int(commitment)
            challenge_int = int(challenge)
            response_int = int(response)
            validation = self._validator.validate(
                public_key_int,
                commitment_int,
                challenge_int,
                response_int,
            )
            if not validation.is_valid:
                return False
            return self._protocol.verify(
                public_key=public_key_int,
                commitment=commitment_int,
                challenge=challenge_int,
                response=response_int,
            )
        except ValueError:
            return False
