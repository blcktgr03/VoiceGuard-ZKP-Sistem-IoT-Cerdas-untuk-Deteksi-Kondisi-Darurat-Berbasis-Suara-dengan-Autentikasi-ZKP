#include "schnorr.h"

#include <bearssl/bearssl_hash.h>

#include "config.h"

static uint32_t modPow(uint32_t base, uint32_t exponent, uint32_t modulus) {
    uint32_t result = 1;
    base %= modulus;
    while (exponent > 0) {
        if (exponent & 1) {
            result = (result * base) % modulus;
        }
        exponent >>= 1;
        base = (base * base) % modulus;
    }
    return result;
}

uint32_t schnorrPublicKey(uint32_t secretKey) {
    return modPow(SCHNORR_G, secretKey % SCHNORR_Q, SCHNORR_P);
}

static uint32_t deriveChallenge(uint32_t commitment, const String &message) {
    String input = String(commitment) + ":" + message;
    uint8_t digest[32];
    br_sha256_context context;

    br_sha256_init(&context);
    br_sha256_update(&context, input.c_str(), input.length());
    br_sha256_out(&context, digest);

    uint32_t value = 0;
    for (uint8_t i = 0; i < 32; ++i) {
        value = ((value * 256) + digest[i]) % SCHNORR_Q;
    }
    return value;
}

SchnorrDeviceProof schnorrCreateCommitment() {
    SchnorrDeviceProof proof;
    proof.nonce = random(1, SCHNORR_Q);
    proof.commitment = modPow(SCHNORR_G, proof.nonce, SCHNORR_P);
    proof.response = 0;
    return proof;
}

void schnorrCompleteProof(SchnorrDeviceProof &proof, uint32_t challenge) {
    // Schnorr math:
    // public key y = g^x mod p, commitment t = g^r mod p.
    // Server sends challenge c. Device answers s = r + c*x mod q.
    proof.response = (proof.nonce + (challenge * DEVICE_SECRET_KEY)) % SCHNORR_Q;
}

bool schnorrVerifyServerProof(const SchnorrServerProof &proof) {
    if (proof.publicKey != SERVER_PUBLIC_KEY) {
        return false;
    }
    if (deriveChallenge(proof.commitment, proof.message) != proof.challenge) {
        return false;
    }

    // Verify g^s == t * y^c mod p, proving the server knows the server secret x.
    uint32_t left = modPow(SCHNORR_G, proof.response, SCHNORR_P);
    uint32_t right = (proof.commitment * modPow(proof.publicKey, proof.challenge, SCHNORR_P)) % SCHNORR_P;
    return left == right;
}
