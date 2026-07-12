from backend.zkp.params import DEMO_PARAMS
from backend.zkp.schnorr import SchnorrProtocol


def test_schnorr_interactive_proof_verifies() -> None:
    """Verify the demo Schnorr equation for a known nonce and secret."""
    protocol = SchnorrProtocol(DEMO_PARAMS)
    secret_key = 5
    nonce = 3
    challenge = 4

    public_key = protocol.public_key_from_secret(secret_key)
    commitment = pow(DEMO_PARAMS.g, nonce, DEMO_PARAMS.p)
    response = protocol.create_interactive_response(secret_key, nonce, challenge)

    assert protocol.verify(public_key, commitment, challenge, response)


def test_schnorr_rejects_wrong_response() -> None:
    """Reject a proof when the response does not satisfy the Schnorr equation."""
    protocol = SchnorrProtocol(DEMO_PARAMS)
    secret_key = 5
    nonce = 3
    challenge = 4

    public_key = protocol.public_key_from_secret(secret_key)
    commitment = pow(DEMO_PARAMS.g, nonce, DEMO_PARAMS.p)
    valid_response = protocol.create_interactive_response(secret_key, nonce, challenge)
    wrong_response = (valid_response + 1) % DEMO_PARAMS.q

    assert not protocol.verify(public_key, commitment, challenge, wrong_response)
