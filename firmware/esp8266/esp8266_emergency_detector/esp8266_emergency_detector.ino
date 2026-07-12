#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <bearssl/bearssl_hash.h>

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

static const char *WIFI_SSID = "laptop";
static const char *WIFI_PASSWORD = "87654321";
static const char *SERVER_BASE_URL = "http://192.168.93.132:8000";
static const char *DEVICE_ID = "esp8266-worker-01";

// Demo Schnorr parameters. Keep them identical to the backend prototype.
static const uint32_t SCHNORR_P = 23;
static const uint32_t SCHNORR_Q = 11;
static const uint32_t SCHNORR_G = 2;
static const uint32_t DEVICE_SECRET_KEY = 5;
static const uint32_t SERVER_PUBLIC_KEY = 13;

static const uint8_t BUZZER_PIN = 14; // GPIO14 corresponds to D5 on NodeMCU

// ---------------------------------------------------------------------------
// Data structures
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Schnorr helpers
// ---------------------------------------------------------------------------

static uint32_t modPow(uint32_t base, uint32_t exponent, uint32_t modulus) {
    uint32_t result = 1;
    base %= modulus;
    while (exponent > 0) {
        if (exponent & 1U) {
            result = (result * base) % modulus;
        }
        exponent >>= 1U;
        base = (base * base) % modulus;
    }
    return result;
}

uint32_t schnorrPublicKey(uint32_t secretKey) {
    return modPow(SCHNORR_G, secretKey % SCHNORR_Q, SCHNORR_P);
}

static uint32_t deriveChallenge(uint32_t commitment, const String &message) {
    // Fiat-Shamir style challenge: hash(commitment || message) mod q.
    String input = String(commitment) + ":" + message;
    uint8_t digest[32];
    br_sha256_context context;

    br_sha256_init(&context);
    br_sha256_update(&context, input.c_str(), input.length());
    br_sha256_out(&context, digest);

    uint32_t value = 0;
    for (uint8_t i = 0; i < 32; ++i) {
        value = ((value * 256U) + digest[i]) % SCHNORR_Q;
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
    // Schnorr relation:
    // y = g^x mod p
    // t = g^r mod p
    // s = r + c*x mod q
    proof.response = (proof.nonce + (challenge * DEVICE_SECRET_KEY)) % SCHNORR_Q;
}

bool schnorrVerifyServerProof(const SchnorrServerProof &proof) {
    if (proof.publicKey != SERVER_PUBLIC_KEY) {
        return false;
    }

    if (deriveChallenge(proof.commitment, proof.message) != proof.challenge) {
        return false;
    }

    // Verify g^s == t * y^c mod p.
    uint32_t left = modPow(SCHNORR_G, proof.response, SCHNORR_P);
    uint32_t right = (proof.commitment * modPow(proof.publicKey, proof.challenge, SCHNORR_P)) % SCHNORR_P;
    return left == right;
}

// ---------------------------------------------------------------------------
// HTTP helpers
// ---------------------------------------------------------------------------

static bool parseJson(const String &payload, JsonDocument &doc) {
    DeserializationError error = deserializeJson(doc, payload);
    if (error) {
        Serial.print("JSON parse failed: ");
        Serial.println(error.c_str());
        return false;
    }
    return true;
}

ChallengeResult requestChallenge(uint32_t commitment) {
    WiFiClient client;
    HTTPClient http;
    ChallengeResult result = {false, 0};

    http.begin(client, String(SERVER_BASE_URL) + "/challenge");
    http.addHeader("Content-Type", "application/json");

    JsonDocument request;
    request["device_id"] = DEVICE_ID;
    request["commitment"] = String(commitment);

    String body;
    serializeJson(request, body);
    int code = http.POST(body);

    if (code == 201) {
        JsonDocument response;
        String payload = http.getString();
        if (parseJson(payload, response)) {
            result.ok = true;
            result.challenge = response["challenge"].as<uint32_t>();
        }
    } else {
        Serial.printf("Challenge request failed: %d\n", code);
    }

    http.end();
    return result;
}

AuthResult verifyProof(uint32_t commitment, uint32_t responseValue) {
    WiFiClient client;
    HTTPClient http;
    AuthResult result = {false, ""};

    http.begin(client, String(SERVER_BASE_URL) + "/verify");
    http.addHeader("Content-Type", "application/json");

    JsonDocument request;
    request["device_id"] = DEVICE_ID;
    request["commitment"] = String(commitment);
    request["response"] = String(responseValue);

    String body;
    serializeJson(request, body);
    int code = http.POST(body);

    if (code == 200) {
        JsonDocument response;
        String payload = http.getString();
        if (parseJson(payload, response)) {
            result.ok = response["authenticated"].as<bool>();
            result.token = response["auth_token"].as<String>();
        }
    } else {
        Serial.printf("Verify request failed: %d\n", code);
    }

    http.end();
    return result;
}

ClassificationResult uploadAudioAndGetClassification(const String &authToken) {
    WiFiClient client;
    HTTPClient http;
    ClassificationResult result;
    result.ok = false;

    http.begin(client, String(SERVER_BASE_URL) + "/api/process/audio");
    http.setTimeout(60000); // 60 seconds timeout for ML processing (Whisper & BERT)
    http.addHeader("X-Auth-Token", authToken);
    http.addHeader("Content-Type", "multipart/form-data; boundary=----esp8266boundary");

    // Placeholder body. Replace with actual bytes captured from MAX4466 later.
    String body = "------esp8266boundary\r\n";
    body += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    body += DEVICE_ID;
    body += "\r\n------esp8266boundary\r\n";
    body += "Content-Disposition: form-data; name=\"audio_file\"; filename=\"sample.raw\"\r\n";
    body += "Content-Type: application/octet-stream\r\n\r\n";
    body += "AUDIO_PLACEHOLDER";
    body += "\r\n------esp8266boundary--\r\n";

    int code = http.POST(body);
    if (code == 201) {
        JsonDocument response;
        String payload = http.getString();
        if (parseJson(payload, response)) {
            result.ok = true;
            result.label = response["classification"]["label"].as<String>();
            result.serverProof.publicKey = response["server_proof"]["public_key"].as<uint32_t>();
            result.serverProof.commitment = response["server_proof"]["commitment"].as<uint32_t>();
            result.serverProof.challenge = response["server_proof"]["challenge"].as<uint32_t>();
            result.serverProof.response = response["server_proof"]["response"].as<uint32_t>();
            result.serverProof.message = response["server_proof"]["message"].as<String>();
        }
    } else {
        Serial.printf("Audio upload failed: %d\n", code);
    }

    http.end();
    return result;
}

// ---------------------------------------------------------------------------
// Runtime
// ---------------------------------------------------------------------------

static void connectWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("Connected: ");
    Serial.println(WiFi.localIP());
}

static void triggerBuzzer() {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(3000);
    digitalWrite(BUZZER_PIN, LOW);
}

void setup() {
    Serial.begin(115200);
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    randomSeed(ESP.getCycleCount());

    connectWiFi();

    Serial.print("Device public key: ");
    Serial.println(schnorrPublicKey(DEVICE_SECRET_KEY));
}

void loop() {
    SchnorrDeviceProof proof = schnorrCreateCommitment();

    ChallengeResult challenge = requestChallenge(proof.commitment);
    if (!challenge.ok) {
        delay(5000);
        return;
    }

    schnorrCompleteProof(proof, challenge.challenge);

    AuthResult auth = verifyProof(proof.commitment, proof.response);
    if (!auth.ok || auth.token.length() == 0) {
        Serial.println("Authentication failed.");
        delay(5000);
        return;
    }

    ClassificationResult classification = uploadAudioAndGetClassification(auth.token);
    if (!classification.ok) {
        delay(5000);
        return;
    }

    bool serverValid = schnorrVerifyServerProof(classification.serverProof);
    if (serverValid && classification.label == "Emergency") {
        triggerBuzzer();
    }

    delay(10000);
}

