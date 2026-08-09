#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <bearssl/bearssl_hash.h>

#include "config.h"

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

static const char *DEVICE_ID = "esp8266-worker-01";

// Demo Schnorr parameters. Keep them identical to the backend prototype.
static const uint32_t SCHNORR_P = 23;
static const uint32_t SCHNORR_Q = 11;
static const uint32_t SCHNORR_G = 2;
static const uint32_t DEVICE_SECRET_KEY = 5;
static const uint32_t SERVER_PUBLIC_KEY = 13;

static const uint8_t BUZZER_PIN = 14; // GPIO14 corresponds to D5 on NodeMCU
static const uint8_t LED_PIN = 12;    // GPIO12 corresponds to D6 on NodeMCU
static const uint8_t MIC_PIN = A0;
static const uint32_t AUDIO_CHUNK_DURATION_MS = 3000; // 3-5 second audio window.
static const uint32_t AUDIO_SAMPLE_RATE_HZ = 8000;
static const uint16_t WAV_HEADER_SIZE = 44;
static const uint16_t AUDIO_BYTES_PER_SAMPLE = 2;
static const uint32_t AUDIO_SAMPLE_COUNT = (AUDIO_SAMPLE_RATE_HZ * AUDIO_CHUNK_DURATION_MS) / 1000;
static const uint32_t WAV_BUFFER_SIZE = WAV_HEADER_SIZE + (AUDIO_SAMPLE_COUNT * AUDIO_BYTES_PER_SAMPLE);
static const uint32_t NEXT_CHUNK_DELAY_MS = 1000;
static const uint16_t AUDIO_BASELINE_SAMPLE_COUNT = 200;
static const uint16_t AUDIO_MIN_PEAK_TO_PEAK = 6;
static const uint16_t AUDIO_ACTIVE_SAMPLE_THRESHOLD = 2;
static const uint16_t AUDIO_MIN_ACTIVE_PERCENT = 1;
static const uint16_t AUDIO_MIN_AVG_ABS_LEVEL = 0;
static const uint16_t AUDIO_ABSOLUTE_SILENCE_PEAK = 3;
static const int16_t AUDIO_TARGET_PCM16_PEAK = 24000;
static const int32_t AUDIO_GAIN_NUMERATOR = 256;
static const int32_t AUDIO_GAIN_DENOMINATOR = 1;
static const char *MULTIPART_BOUNDARY = "----esp8266boundary";

static void signalRecordingStart();
static void signalRecordingEnd();

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
// Audio helpers
// ---------------------------------------------------------------------------

static void writeLe16(uint8_t *buffer, size_t offset, uint16_t value) {
    buffer[offset] = value & 0xFF;
    buffer[offset + 1] = (value >> 8) & 0xFF;
}

static void writeLe32(uint8_t *buffer, size_t offset, uint32_t value) {
    buffer[offset] = value & 0xFF;
    buffer[offset + 1] = (value >> 8) & 0xFF;
    buffer[offset + 2] = (value >> 16) & 0xFF;
    buffer[offset + 3] = (value >> 24) & 0xFF;
}

static void writeWavHeader(uint8_t *buffer, uint32_t dataSize) {
    memcpy(buffer + 0, "RIFF", 4);
    writeLe32(buffer, 4, 36 + dataSize);
    memcpy(buffer + 8, "WAVE", 4);
    memcpy(buffer + 12, "fmt ", 4);
    writeLe32(buffer, 16, 16);
    writeLe16(buffer, 20, 1); // PCM
    writeLe16(buffer, 22, 1); // mono
    writeLe32(buffer, 24, AUDIO_SAMPLE_RATE_HZ);
    writeLe32(buffer, 28, AUDIO_SAMPLE_RATE_HZ * AUDIO_BYTES_PER_SAMPLE);
    writeLe16(buffer, 32, AUDIO_BYTES_PER_SAMPLE); // block align
    writeLe16(buffer, 34, 16); // bits per sample
    memcpy(buffer + 36, "data", 4);
    writeLe32(buffer, 40, dataSize);
}

static int32_t estimateMicBaseline() {
    uint32_t total = 0;
    for (uint16_t i = 0; i < AUDIO_BASELINE_SAMPLE_COUNT; ++i) {
        total += analogRead(MIC_PIN);
        delayMicroseconds(250);
        yield();
    }
    return total / AUDIO_BASELINE_SAMPLE_COUNT;
}

static int16_t adcToPcm16(uint16_t adcValue, int32_t baseline) {
    // Center the biased MAX4466 signal around zero, then expand it into 16-bit PCM.
    int32_t centered = static_cast<int32_t>(adcValue) - baseline;
    int32_t pcm = (centered * AUDIO_GAIN_NUMERATOR) / AUDIO_GAIN_DENOMINATOR;
    if (pcm < -32768) {
        pcm = -32768;
    }
    if (pcm > 32767) {
        pcm = 32767;
    }
    return static_cast<int16_t>(pcm);
}

static void writePcm16(uint8_t *buffer, uint32_t sampleIndex, int16_t value) {
    size_t offset = WAV_HEADER_SIZE + (sampleIndex * AUDIO_BYTES_PER_SAMPLE);
    buffer[offset] = value & 0xFF;
    buffer[offset + 1] = (value >> 8) & 0xFF;
}

static int16_t readPcm16(uint8_t *buffer, uint32_t sampleIndex) {
    size_t offset = WAV_HEADER_SIZE + (sampleIndex * AUDIO_BYTES_PER_SAMPLE);
    return static_cast<int16_t>(buffer[offset] | (buffer[offset + 1] << 8));
}

static void normalizePcm16(uint8_t *wavBuffer, int16_t minPcm, int16_t maxPcm) {
    int32_t currentPeak = max(abs(static_cast<int32_t>(minPcm)), abs(static_cast<int32_t>(maxPcm)));
    if (currentPeak == 0 || currentPeak >= AUDIO_TARGET_PCM16_PEAK) {
        return;
    }

    uint16_t scale = AUDIO_TARGET_PCM16_PEAK / currentPeak;
    if (scale < 2) {
        return;
    }
    if (scale > 10) {
        scale = 10;
    }

    for (uint32_t i = 0; i < AUDIO_SAMPLE_COUNT; ++i) {
        int32_t boosted = static_cast<int32_t>(readPcm16(wavBuffer, i)) * scale;
        if (boosted < -32768) {
            boosted = -32768;
        }
        if (boosted > 32767) {
            boosted = 32767;
        }
        writePcm16(wavBuffer, i, static_cast<int16_t>(boosted));
    }
    Serial.printf("PCM normalized with scale=%u\n", scale);
}

static bool captureAudioChunkWav(uint8_t *wavBuffer, size_t wavBufferSize, int32_t baseline) {
    if (wavBufferSize < WAV_BUFFER_SIZE) {
        return false;
    }

    writeWavHeader(wavBuffer, AUDIO_SAMPLE_COUNT * AUDIO_BYTES_PER_SAMPLE);

    const uint32_t intervalUs = 1000000UL / AUDIO_SAMPLE_RATE_HZ;
    uint32_t nextSampleAt = micros();
    uint16_t minSample = 1023;
    uint16_t maxSample = 0;
    uint32_t totalSample = 0;
    uint32_t totalAbsCentered = 0;
    uint32_t activeSampleCount = 0;
    int16_t minPcm = 32767;
    int16_t maxPcm = -32768;

    for (uint32_t i = 0; i < AUDIO_SAMPLE_COUNT; ++i) {
        while ((int32_t)(micros() - nextSampleAt) < 0) {
            yield();
        }

        uint16_t sample = analogRead(MIC_PIN);
        int32_t centered = static_cast<int32_t>(sample) - baseline;
        uint32_t absCentered = abs(centered);
        totalAbsCentered += absCentered;
        if (absCentered >= AUDIO_ACTIVE_SAMPLE_THRESHOLD) {
            activeSampleCount++;
        }
        int16_t pcm = adcToPcm16(sample, baseline);
        minSample = min(minSample, sample);
        maxSample = max(maxSample, sample);
        totalSample += sample;
        minPcm = min(minPcm, pcm);
        maxPcm = max(maxPcm, pcm);
        writePcm16(wavBuffer, i, pcm);
        nextSampleAt += intervalUs;
    }

    uint16_t peakToPeak = maxSample - minSample;
    uint32_t avgAbsLevel = totalAbsCentered / AUDIO_SAMPLE_COUNT;
    uint32_t activePercent = (activeSampleCount * 100UL) / AUDIO_SAMPLE_COUNT;
    Serial.printf(
        "Captured %lu samples @ %lu Hz, ADC min=%u max=%u avg=%lu baseline=%ld peak=%u avgAbs=%lu active=%lu%% PCM16 min=%d max=%d\n",
        AUDIO_SAMPLE_COUNT,
        AUDIO_SAMPLE_RATE_HZ,
        minSample,
        maxSample,
        totalSample / AUDIO_SAMPLE_COUNT,
        baseline,
        peakToPeak,
        avgAbsLevel,
        activePercent,
        minPcm,
        maxPcm);

    if (peakToPeak <= AUDIO_ABSOLUTE_SILENCE_PEAK) {
        Serial.println("Audio ignored: voice signal is too weak.");
        return false;
    }

    normalizePcm16(wavBuffer, minPcm, maxPcm);
    return true;
}

static bool streamAudioChunkWav(WiFiClient &client, int32_t baseline) {
    uint8_t wavHeader[WAV_HEADER_SIZE];
    writeWavHeader(wavHeader, AUDIO_SAMPLE_COUNT * AUDIO_BYTES_PER_SAMPLE);
    if (client.write(wavHeader, WAV_HEADER_SIZE) != WAV_HEADER_SIZE) {
        Serial.println("Audio stream failed: WAV header write failed.");
        return false;
    }

    const uint32_t intervalUs = 1000000UL / AUDIO_SAMPLE_RATE_HZ;
    uint32_t nextSampleAt = micros();
    uint16_t minSample = 1023;
    uint16_t maxSample = 0;
    uint32_t totalSample = 0;
    uint32_t totalAbsCentered = 0;
    uint32_t activeSampleCount = 0;
    int16_t minPcm = 32767;
    int16_t maxPcm = -32768;
    uint8_t chunk[256];
    size_t chunkIndex = 0;

    for (uint32_t i = 0; i < AUDIO_SAMPLE_COUNT; ++i) {
        while ((int32_t)(micros() - nextSampleAt) < 0) {
            yield();
        }

        uint16_t sample = analogRead(MIC_PIN);
        int32_t centered = static_cast<int32_t>(sample) - baseline;
        uint32_t absCentered = abs(centered);
        totalAbsCentered += absCentered;
        if (absCentered >= AUDIO_ACTIVE_SAMPLE_THRESHOLD) {
            activeSampleCount++;
        }

        int16_t pcm = adcToPcm16(sample, baseline);
        minSample = min(minSample, sample);
        maxSample = max(maxSample, sample);
        totalSample += sample;
        minPcm = min(minPcm, pcm);
        maxPcm = max(maxPcm, pcm);

        chunk[chunkIndex++] = pcm & 0xFF;
        chunk[chunkIndex++] = (pcm >> 8) & 0xFF;
        if (chunkIndex >= sizeof(chunk)) {
            if (client.write(chunk, chunkIndex) != chunkIndex) {
                Serial.println("Audio stream failed: sample write failed.");
                return false;
            }
            chunkIndex = 0;
        }
        nextSampleAt += intervalUs;
    }

    if (chunkIndex > 0 && client.write(chunk, chunkIndex) != chunkIndex) {
        Serial.println("Audio stream failed: final sample write failed.");
        return false;
    }

    uint16_t peakToPeak = maxSample - minSample;
    uint32_t avgAbsLevel = totalAbsCentered / AUDIO_SAMPLE_COUNT;
    uint32_t activePercent = (activeSampleCount * 100UL) / AUDIO_SAMPLE_COUNT;
    Serial.printf(
        "Streamed %lu samples @ %lu Hz, ADC min=%u max=%u avg=%lu baseline=%ld peak=%u avgAbs=%lu active=%lu%% PCM16 min=%d max=%d\n",
        AUDIO_SAMPLE_COUNT,
        AUDIO_SAMPLE_RATE_HZ,
        minSample,
        maxSample,
        totalSample / AUDIO_SAMPLE_COUNT,
        baseline,
        peakToPeak,
        avgAbsLevel,
        activePercent,
        minPcm,
        maxPcm);

    return true;
}

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

static const char *httpErrorName(int code) {
    switch (code) {
    case HTTPC_ERROR_CONNECTION_REFUSED:
        return "connection refused";
    case HTTPC_ERROR_SEND_HEADER_FAILED:
        return "send header failed";
    case HTTPC_ERROR_SEND_PAYLOAD_FAILED:
        return "send payload failed";
    case HTTPC_ERROR_NOT_CONNECTED:
        return "not connected";
    case HTTPC_ERROR_CONNECTION_LOST:
        return "connection lost";
    case HTTPC_ERROR_NO_STREAM:
        return "no stream";
    case HTTPC_ERROR_NO_HTTP_SERVER:
        return "no HTTP server";
    case HTTPC_ERROR_TOO_LESS_RAM:
        return "too little RAM";
    case HTTPC_ERROR_ENCODING:
        return "encoding error";
    case HTTPC_ERROR_STREAM_WRITE:
        return "stream write failed";
    case HTTPC_ERROR_READ_TIMEOUT:
        return "read timeout";
    default:
        return "unknown HTTP error";
    }
}

static bool parseServerAddress(String &host, uint16_t &port) {
    String baseUrl = SERVER_BASE_URL;
    baseUrl.replace("http://", "");
    int slashIndex = baseUrl.indexOf('/');
    if (slashIndex >= 0) {
        baseUrl = baseUrl.substring(0, slashIndex);
    }

    int colonIndex = baseUrl.indexOf(':');
    if (colonIndex >= 0) {
        host = baseUrl.substring(0, colonIndex);
        port = static_cast<uint16_t>(baseUrl.substring(colonIndex + 1).toInt());
    } else {
        host = baseUrl;
        port = 80;
    }

    return host.length() > 0 && port > 0;
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
    ClassificationResult result;
    result.ok = false;

    String host;
    uint16_t port = 80;
    if (!parseServerAddress(host, port)) {
        Serial.println("Invalid SERVER_BASE_URL.");
        return result;
    }

    String preamble = "--";
    preamble += MULTIPART_BOUNDARY;
    preamble += "\r\nContent-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    preamble += DEVICE_ID;
    preamble += "\r\n--";
    preamble += MULTIPART_BOUNDARY;
    preamble += "\r\nContent-Disposition: form-data; name=\"audio_file\"; filename=\"chunk.wav\"\r\n";
    preamble += "Content-Type: audio/wav\r\n\r\n";

    String closing = "\r\n--";
    closing += MULTIPART_BOUNDARY;
    closing += "--\r\n";

    const size_t preambleSize = preamble.length();
    const size_t closingSize = closing.length();
    const size_t multipartSize = preambleSize + WAV_BUFFER_SIZE + closingSize;
    Serial.printf("Free heap before streaming upload: %u bytes\n", ESP.getFreeHeap());

    Serial.printf("Connecting to %s:%u for streaming upload...\n", host.c_str(), port);
    if (!client.connect(host.c_str(), port)) {
        Serial.println("Audio upload failed: cannot connect to backend.");
        return result;
    }

    client.setTimeout(120000);
    client.print("POST /api/process/audio HTTP/1.1\r\n");
    client.print("Host: ");
    client.print(host);
    client.print(":");
    client.print(port);
    client.print("\r\n");
    client.print("X-Auth-Token: ");
    client.print(authToken);
    client.print("\r\n");
    client.print("Content-Type: multipart/form-data; boundary=");
    client.print(MULTIPART_BOUNDARY);
    client.print("\r\n");
    client.print("Content-Length: ");
    client.print(multipartSize);
    client.print("\r\n");
    client.print("Connection: close\r\n\r\n");

    Serial.printf("Uploading WAV chunk: %u bytes\n", static_cast<unsigned int>(multipartSize));
    client.write(reinterpret_cast<const uint8_t *>(preamble.c_str()), preambleSize);

    int32_t baseline = estimateMicBaseline();
    Serial.printf("Mic baseline: %ld\n", baseline);

    signalRecordingStart();
    if (!streamAudioChunkWav(client, baseline)) {
        Serial.println("Audio capture/upload failed.");
        signalRecordingEnd();
        client.stop();
        return result;
    }
    signalRecordingEnd();

    client.write(reinterpret_cast<const uint8_t *>(closing.c_str()), closingSize);

    String statusLine = client.readStringUntil('\n');
    statusLine.trim();
    Serial.println(statusLine);

    int code = 0;
    int firstSpace = statusLine.indexOf(' ');
    if (firstSpace >= 0 && statusLine.length() >= firstSpace + 4) {
        code = statusLine.substring(firstSpace + 1, firstSpace + 4).toInt();
    }

    int contentLength = -1;
    while (client.connected()) {
        String headerLine = client.readStringUntil('\n');
        headerLine.trim();
        if (headerLine.length() == 0) {
            break;
        }
        String lowerHeader = headerLine;
        lowerHeader.toLowerCase();
        if (lowerHeader.startsWith("content-length:")) {
            contentLength = headerLine.substring(headerLine.indexOf(':') + 1).toInt();
        }
    }

    String payload;
    if (contentLength >= 0) {
        payload.reserve(contentLength);
        uint32_t deadline = millis() + 15000;
        while (payload.length() < static_cast<size_t>(contentLength) && millis() < deadline) {
            while (client.available() && payload.length() < static_cast<size_t>(contentLength)) {
                payload += static_cast<char>(client.read());
                deadline = millis() + 15000;
            }
            yield();
        }
    } else {
        uint32_t deadline = millis() + 15000;
        while ((client.connected() || client.available()) && millis() < deadline) {
            while (client.available()) {
                payload += static_cast<char>(client.read());
                deadline = millis() + 15000;
            }
            yield();
        }
    }
    client.stop();

    if (code == 201) {
        JsonDocument response;
        if (parseJson(payload, response)) {
            result.ok = true;
            result.label = response["classification"]["label"].as<String>();
            float confidence = response["classification"]["confidence"].as<float>();
            Serial.printf("Classification: %s confidence=%.3f\n", result.label.c_str(), confidence);
            result.serverProof.publicKey = response["server_proof"]["public_key"].as<uint32_t>();
            result.serverProof.commitment = response["server_proof"]["commitment"].as<uint32_t>();
            result.serverProof.challenge = response["server_proof"]["challenge"].as<uint32_t>();
            result.serverProof.response = response["server_proof"]["response"].as<uint32_t>();
            result.serverProof.message = response["server_proof"]["message"].as<String>();
        }
    } else {
        Serial.printf("Audio upload failed with HTTP status: %d\n", code);
        if (payload.length() > 0) {
            Serial.println(payload);
        }
    }

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

static void beep(uint16_t durationMs) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(durationMs);
    digitalWrite(BUZZER_PIN, LOW);
}

static void signalRecordingStart() {
    Serial.println();
    Serial.println("=== BICARA SEKARANG ===");
    Serial.printf("Rekam audio selama %lu detik...\n", AUDIO_CHUNK_DURATION_MS / 1000);
    digitalWrite(LED_PIN, HIGH);
}

static void signalRecordingEnd() {
    digitalWrite(LED_PIN, LOW);
    Serial.println("=== REKAMAN SELESAI, SEDANG UPLOAD/PROSES ===");
}

static void triggerEmergencyAlert() {
    digitalWrite(BUZZER_PIN, HIGH);
    digitalWrite(LED_PIN, HIGH);
    delay(3000);
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, HIGH);
}

void setup() {
    Serial.begin(115200);
    pinMode(MIC_PIN, INPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);
    randomSeed(ESP.getCycleCount());

    connectWiFi();

    Serial.print("Device public key: ");
    Serial.println(schnorrPublicKey(DEVICE_SECRET_KEY));
}

void loop() {
    Serial.println();
    Serial.println("--- Mulai siklus rekam baru ---");
    SchnorrDeviceProof proof = schnorrCreateCommitment();

    ChallengeResult challenge = requestChallenge(proof.commitment);
    if (!challenge.ok) {
        Serial.println("Challenge failed. Retry in 5 seconds.");
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
        Serial.println("Classification failed. Retry in 5 seconds.");
        delay(5000);
        return;
    }

    bool serverValid = schnorrVerifyServerProof(classification.serverProof);
    Serial.printf("Server proof valid: %s\n", serverValid ? "yes" : "no");
    if (serverValid && classification.label == "Emergency") {
        triggerEmergencyAlert();
    }

    Serial.printf("Siklus selesai. Rekam lagi dalam %lu ms.\n", NEXT_CHUNK_DELAY_MS);
    delay(NEXT_CHUNK_DELAY_MS);
}
