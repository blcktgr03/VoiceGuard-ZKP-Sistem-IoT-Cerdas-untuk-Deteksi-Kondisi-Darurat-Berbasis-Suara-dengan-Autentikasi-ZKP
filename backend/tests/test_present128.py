import base64

import pytest

from backend.crypto.present128 import (
    PresentCipherError,
    decrypt_audio_payload,
    encrypt_audio_payload,
    present128_ctr_crypt,
    present128_encrypt_block,
)


def test_present128_known_zero_vector() -> None:
    """Check PRESENT-128 against the standard all-zero test vector."""
    ciphertext = present128_encrypt_block(bytes(8), bytes(16))
    assert ciphertext.hex() == "96db702a2e6900af"


def test_present128_ctr_round_trip() -> None:
    """CTR mode decrypts by applying the same operation again."""
    nonce = bytes.fromhex("0000000000000001")
    plaintext = b"RIFF demo wav bytes for VoiceGuard-ZKP"

    ciphertext = present128_ctr_crypt(plaintext, nonce)
    recovered = present128_ctr_crypt(ciphertext, nonce)

    assert ciphertext != plaintext
    assert recovered == plaintext


def test_present128_payload_round_trip() -> None:
    """Encrypted JSON payloads can be recovered by the backend."""
    plaintext = b"RIFF" + bytes(range(32))
    payload = encrypt_audio_payload(
        plaintext,
        device_id="esp32s3-inmp441-worker-01",
        nonce=bytes.fromhex("0000000000000007"),
    )

    recovered = decrypt_audio_payload(**payload)

    assert recovered == plaintext


def test_present128_payload_rejects_tampering() -> None:
    """Changing the ciphertext invalidates the HMAC authentication tag."""
    payload = encrypt_audio_payload(
        b"audio",
        device_id="esp32s3-inmp441-worker-01",
        nonce=bytes.fromhex("0000000000000009"),
    )
    ciphertext = bytearray(base64.b64decode(payload["ciphertext_b64"]))
    ciphertext[0] ^= 0x01
    payload["ciphertext_b64"] = base64.b64encode(ciphertext).decode("ascii")

    with pytest.raises(PresentCipherError):
        decrypt_audio_payload(**payload)
