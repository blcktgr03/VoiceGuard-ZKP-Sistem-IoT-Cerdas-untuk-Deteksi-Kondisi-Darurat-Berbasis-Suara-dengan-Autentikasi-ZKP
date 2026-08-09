#pragma once

#include <Arduino.h>

#include "schnorr.h"

struct ChallengeResult {
    bool ok;
    uint32_t challenge;
};

struct AuthResult {
    bool ok;
    String token;
};

struct ClassificationResult {
    bool ok;
    String label;
    SchnorrServerProof serverProof;
};

ChallengeResult requestChallenge(uint32_t commitment);
AuthResult verifyProof(uint32_t commitment, uint32_t response);
ClassificationResult uploadAudioAndGetClassification(const String &authToken);

