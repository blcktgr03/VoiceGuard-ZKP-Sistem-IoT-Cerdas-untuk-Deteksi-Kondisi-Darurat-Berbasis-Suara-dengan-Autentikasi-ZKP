#pragma once

#include <Arduino.h>

struct SchnorrDeviceProof {
    uint32_t nonce;
    uint32_t commitment;
    uint32_t response;
};

struct SchnorrServerProof {
    uint32_t publicKey;
    uint32_t commitment;
    uint32_t challenge;
    uint32_t response;
    String message;
};

uint32_t schnorrPublicKey(uint32_t secretKey);
SchnorrDeviceProof schnorrCreateCommitment();
void schnorrCompleteProof(SchnorrDeviceProof &proof, uint32_t challenge);
bool schnorrVerifyServerProof(const SchnorrServerProof &proof);

