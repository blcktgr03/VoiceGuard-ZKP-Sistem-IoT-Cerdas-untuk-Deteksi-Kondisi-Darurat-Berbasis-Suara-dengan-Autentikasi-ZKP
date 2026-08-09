"""PRESENT-128 encryption helpers for the IoT audio upload prototype.

This module intentionally keeps the key hardcoded because the current use case
is an academic prototype/demo. For real deployments, move keys to secure device
provisioning and server-side secret management.
"""

from __future__ import annotations

import base64
import hashlib
import hmac


BLOCK_SIZE_BYTES = 8
ROUNDS = 31
PRESENT128_KEY_BYTES = bytes.fromhex("00112233445566778899aabbccddeeff")
PRESENT128_HMAC_KEY_BYTES = bytes.fromhex(
    "102132435465768798a9babbdcddfeef00112233445566778899aabbccddeeff"
)

_SBOX = (0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2)


class PresentCipherError(ValueError):
    """Raised when encrypted PRESENT payloads cannot be validated or decrypted."""


def encrypt_audio_payload(
    plaintext: bytes,
    *,
    device_id: str,
    nonce: bytes,
    filename: str = "chunk.wav",
    mime_type: str = "audio/wav",
) -> dict[str, str]:
    """Encrypt bytes into a JSON-safe PRESENT-128 CTR payload with HMAC integrity."""
    _validate_nonce(nonce)
    ciphertext = present128_ctr_crypt(plaintext, nonce)
    tag = _authentication_tag(
        device_id=device_id,
        nonce=nonce,
        ciphertext=ciphertext,
        filename=filename,
        mime_type=mime_type,
    )
    return {
        "device_id": device_id,
        "nonce_hex": nonce.hex(),
        "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
        "tag_hex": tag.hex(),
        "filename": filename,
        "mime_type": mime_type,
    }


def decrypt_audio_payload(
    *,
    device_id: str,
    nonce_hex: str,
    ciphertext_b64: str,
    tag_hex: str,
    filename: str = "chunk.wav",
    mime_type: str = "audio/wav",
) -> bytes:
    """Validate and decrypt a PRESENT-128 CTR audio payload."""
    try:
        nonce = bytes.fromhex(nonce_hex)
        ciphertext = base64.b64decode(ciphertext_b64, validate=True)
        provided_tag = bytes.fromhex(tag_hex)
    except ValueError as exc:
        raise PresentCipherError("Encrypted payload encoding is invalid.") from exc

    _validate_nonce(nonce)
    expected_tag = _authentication_tag(
        device_id=device_id,
        nonce=nonce,
        ciphertext=ciphertext,
        filename=filename,
        mime_type=mime_type,
    )
    if not hmac.compare_digest(provided_tag, expected_tag):
        raise PresentCipherError("Encrypted payload authentication tag is invalid.")

    return present128_ctr_crypt(ciphertext, nonce)


def present128_ctr_crypt(data: bytes, nonce: bytes, key: bytes = PRESENT128_KEY_BYTES) -> bytes:
    """Encrypt or decrypt bytes using PRESENT-128 in CTR mode."""
    _validate_key(key)
    _validate_nonce(nonce)

    counter = int.from_bytes(nonce, "big")
    output = bytearray()
    round_keys = _generate_round_keys(key)

    for offset in range(0, len(data), BLOCK_SIZE_BYTES):
        block = data[offset : offset + BLOCK_SIZE_BYTES]
        keystream = _encrypt_block(counter.to_bytes(BLOCK_SIZE_BYTES, "big"), round_keys)
        output.extend(byte ^ stream for byte, stream in zip(block, keystream))
        counter = (counter + 1) & 0xFFFFFFFFFFFFFFFF

    return bytes(output)


def present128_encrypt_block(block: bytes, key: bytes = PRESENT128_KEY_BYTES) -> bytes:
    """Encrypt one 64-bit block using PRESENT-128."""
    if len(block) != BLOCK_SIZE_BYTES:
        raise PresentCipherError("PRESENT block must be exactly 8 bytes.")
    _validate_key(key)
    return _encrypt_block(block, _generate_round_keys(key))


def _encrypt_block(block: bytes, round_keys: tuple[int, ...]) -> bytes:
    state = int.from_bytes(block, "big")
    for round_index in range(ROUNDS):
        state ^= round_keys[round_index]
        state = _sbox_layer(state)
        state = _player(state)
    state ^= round_keys[ROUNDS]
    return state.to_bytes(BLOCK_SIZE_BYTES, "big")


def _generate_round_keys(key: bytes) -> tuple[int, ...]:
    key_register = int.from_bytes(key, "big")
    round_keys: list[int] = []
    key_mask = (1 << 128) - 1

    for round_counter in range(1, ROUNDS + 2):
        round_keys.append(key_register >> 64)
        if round_counter == ROUNDS + 1:
            break

        key_register = ((key_register << 61) & key_mask) | (key_register >> 67)
        top_nibble = _SBOX[(key_register >> 124) & 0xF]
        second_nibble = _SBOX[(key_register >> 120) & 0xF]
        key_register &= (1 << 120) - 1
        key_register |= top_nibble << 124
        key_register |= second_nibble << 120
        key_register ^= round_counter << 62

    return tuple(round_keys)


def _sbox_layer(state: int) -> int:
    output = 0
    for index in range(16):
        nibble = (state >> (index * 4)) & 0xF
        output |= _SBOX[nibble] << (index * 4)
    return output


def _player(state: int) -> int:
    output = 0
    for bit_index in range(63):
        bit = (state >> bit_index) & 1
        output |= bit << ((16 * bit_index) % 63)
    output |= ((state >> 63) & 1) << 63
    return output


def _authentication_tag(
    *,
    device_id: str,
    nonce: bytes,
    ciphertext: bytes,
    filename: str,
    mime_type: str,
) -> bytes:
    associated_data = "|".join((device_id, filename, mime_type)).encode("utf-8")
    message = associated_data + b"\x00" + nonce + b"\x00" + ciphertext
    return hmac.new(PRESENT128_HMAC_KEY_BYTES, message, hashlib.sha256).digest()


def _validate_key(key: bytes) -> None:
    if len(key) != 16:
        raise PresentCipherError("PRESENT-128 key must be exactly 16 bytes.")


def _validate_nonce(nonce: bytes) -> None:
    if len(nonce) != BLOCK_SIZE_BYTES:
        raise PresentCipherError("PRESENT CTR nonce must be exactly 8 bytes.")
