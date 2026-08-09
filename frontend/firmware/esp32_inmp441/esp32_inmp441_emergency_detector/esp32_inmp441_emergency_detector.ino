#include <Arduino.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <driver/i2s.h>
#include <mbedtls/sha256.h>

#include "config.h"

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

static const char *DEVICE_ID = "esp32s3-inmp441-worker-01";

// Demo Schnorr parameters. Keep them identical to the backend prototype.
static const uint32_t SCHNORR_P = 23;
static const uint32_t SCHNORR_Q = 11;
static const uint32_t SCHNORR_G = 2;
static const uint32_t DEVICE_SECRET_KEY = 5;
static const uint32_t SERVER_PUBLIC_KEY = 13;

// INMP441 pinout for ESP32-S3.
static const int I2S_BCLK_PIN = 18; // INMP441 SCK / BCLK
static const int I2S_WS_PIN = 17;   // INMP441 WS / LRCL
static const int I2S_SD_PIN = 16;   // INMP441 SD / DOUT

static const uint8_t LED_PIN = 12;
static const uint8_t BUZZER_PIN = 9;
static const bool BUZZER_ACTIVE_HIGH = true;

static const uint32_t AUDIO_CHUNK_DURATION_MS = 3000;
static const uint32_t AUDIO_SAMPLE_RATE_HZ = 16000;
static const uint16_t WAV_HEADER_SIZE = 44;
static const uint16_t AUDIO_BYTES_PER_SAMPLE = 2;
static const uint32_t AUDIO_SAMPLE_COUNT = (AUDIO_SAMPLE_RATE_HZ * AUDIO_CHUNK_DURATION_MS) / 1000;
static const uint32_t WAV_DATA_SIZE = AUDIO_SAMPLE_COUNT * AUDIO_BYTES_PER_SAMPLE;
static const uint32_t WAV_BUFFER_SIZE = WAV_HEADER_SIZE + WAV_DATA_SIZE;
static const uint32_t NEXT_CHUNK_DELAY_MS = 10;
static const uint32_t ERROR_RETRY_DELAY_MS = 2000;
static const char *MULTIPART_BOUNDARY = "----esp32inmp441boundary";

// INMP441 outputs 24-bit audio packed in a 32-bit I2S word.
// If the audio is too quiet/noisy, tune this value between 10 and 16.
static const uint8_t I2S_TO_PCM16_SHIFT = 13;

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
    bool emergencyDetected;
    String label;
    SchnorrServerProof serverProof;
};

// ---------------------------------------------------------------------------
// WAV helpers
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
    writeLe16(buffer, 32, AUDIO_BYTES_PER_SAMPLE);
    writeLe16(buffer, 34, 16); // 16-bit PCM
    memcpy(buffer + 36, "data", 4);
    writeLe32(buffer, 40, dataSize);
}

static int16_t i2sWordToPcm16(int32_t sample) {
    int32_t pcm = sample >> I2S_TO_PCM16_SHIFT;
    if (pcm < -32768) {
        pcm = -32768;
    }
    if (pcm > 32767) {
        pcm = 32767;
    }
    return static_cast<int16_t>(pcm);
}

// ---------------------------------------------------------------------------
// I2S microphone helpers
// ---------------------------------------------------------------------------

static void setupI2SMicrophone() {
    i2s_config_t i2sConfig = {};
    i2sConfig.mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX);
    i2sConfig.sample_rate = AUDIO_SAMPLE_RATE_HZ;
    i2sConfig.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
    i2sConfig.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
    i2sConfig.communication_format = I2S_COMM_FORMAT_STAND_I2S;
    i2sConfig.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
    i2sConfig.dma_buf_count = 8;
    i2sConfig.dma_buf_len = 256;
    i2sConfig.use_apll = false;
    i2sConfig.tx_desc_auto_clear = false;
    i2sConfig.fixed_mclk = 0;

    i2s_pin_config_t pinConfig = {};
    pinConfig.bck_io_num = I2S_BCLK_PIN;
    pinConfig.ws_io_num = I2S_WS_PIN;
    pinConfig.data_out_num = I2S_PIN_NO_CHANGE;
    pinConfig.data_in_num = I2S_SD_PIN;

    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2sConfig, 0, nullptr);
    if (result != ESP_OK) {
        Serial.printf("I2S driver install failed: %d\n", result);
        return;
    }

    result = i2s_set_pin(I2S_NUM_0, &pinConfig);
    if (result != ESP_OK) {
        Serial.printf("I2S pin setup failed: %d\n", result);
        return;
    }

    i2s_zero_dma_buffer(I2S_NUM_0);
    Serial.println("INMP441 I2S microphone ready.");
}

static void flushI2SInput() {
    int32_t discard[128];
    size_t bytesRead = 0;
    uint32_t start = millis();
    while (millis() - start < 60) {
        i2s_read(I2S_NUM_0, discard, sizeof(discard), &bytesRead, 20 / portTICK_PERIOD_MS);
        yield();
    }
}

static bool streamAudioChunkWav(WiFiClient &client) {
    uint8_t wavHeader[WAV_HEADER_SIZE];
    writeWavHeader(wavHeader, WAV_DATA_SIZE);
    if (client.write(wavHeader, WAV_HEADER_SIZE) != WAV_HEADER_SIZE) {
        Serial.println("Audio stream failed: WAV header write failed.");
        return false;
    }

    int32_t i2sSamples[128];
    uint8_t pcmChunk[sizeof(i2sSamples) / sizeof(i2sSamples[0]) * AUDIO_BYTES_PER_SAMPLE];
    uint32_t writtenSamples = 0;
    int16_t minPcm = 32767;
    int16_t maxPcm = -32768;
    uint32_t activeSamples = 0;
    uint32_t totalAbs = 0;

    while (writtenSamples < AUDIO_SAMPLE_COUNT) {
        size_t bytesRead = 0;
        esp_err_t result = i2s_read(
            I2S_NUM_0,
            i2sSamples,
            sizeof(i2sSamples),
            &bytesRead,
            100 / portTICK_PERIOD_MS);

        if (result != ESP_OK || bytesRead == 0) {
            Serial.printf("I2S read failed: %d bytes=%u\n", result, static_cast<unsigned int>(bytesRead));
            return false;
        }

        size_t sampleCount = bytesRead / sizeof(int32_t);
        size_t pcmIndex = 0;
        for (size_t i = 0; i < sampleCount && writtenSamples < AUDIO_SAMPLE_COUNT; ++i) {
            int16_t pcm = i2sWordToPcm16(i2sSamples[i]);
            minPcm = min(minPcm, pcm);
            maxPcm = max(maxPcm, pcm);

            uint32_t absPcm = abs(static_cast<int32_t>(pcm));
            totalAbs += absPcm;
            if (absPcm > 700) {
                activeSamples++;
            }

            pcmChunk[pcmIndex++] = pcm & 0xFF;
            pcmChunk[pcmIndex++] = (pcm >> 8) & 0xFF;
            writtenSamples++;
        }

        if (pcmIndex > 0 && client.write(pcmChunk, pcmIndex) != pcmIndex) {
            Serial.println("Audio stream failed: sample write failed.");
            return false;
        }

        yield();
    }

    uint32_t avgAbs = totalAbs / AUDIO_SAMPLE_COUNT;
    uint32_t activePercent = (activeSamples * 100UL) / AUDIO_SAMPLE_COUNT;
    Serial.printf(
        "Streamed %lu samples @ %lu Hz, PCM16 min=%d max=%d avgAbs=%lu active=%lu%%\n",
        AUDIO_SAMPLE_COUNT,
        AUDIO_SAMPLE_RATE_HZ,
        minPcm,
        maxPcm,
        avgAbs,
        activePercent);

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
    String input = String(commitment) + ":" + message;
    uint8_t digest[32];
    mbedtls_sha256(
        reinterpret_cast<const unsigned char *>(input.c_str()),
        input.length(),
        digest,
        0);

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
    proof.response = (proof.nonce + (challenge * DEVICE_SECRET_KEY)) % SCHNORR_Q;
}

bool schnorrVerifyServerProof(const SchnorrServerProof &proof) {
    if (proof.publicKey != SERVER_PUBLIC_KEY) {
        return false;
    }
    if (deriveChallenge(proof.commitment, proof.message) != proof.challenge) {
        return false;
    }

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
    result.emergencyDetected = false;

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

    Serial.printf("Connecting to %s:%u for INMP441 upload...\n", host.c_str(), port);
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

    Serial.printf("Uploading INMP441 WAV chunk: %u bytes\n", static_cast<unsigned int>(multipartSize));
    client.write(reinterpret_cast<const uint8_t *>(preamble.c_str()), preambleSize);

    flushI2SInput();
    Serial.println("=== BICARA SEKARANG ===");
    digitalWrite(LED_PIN, HIGH);
    if (!streamAudioChunkWav(client)) {
        digitalWrite(LED_PIN, LOW);
        client.stop();
        return result;
    }
    digitalWrite(LED_PIN, LOW);
    Serial.println("=== REKAMAN SELESAI, SEDANG UPLOAD/PROSES ===");

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
    while (client.connected() || client.available()) {
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
            result.emergencyDetected = response["emergency_detected"] | false;
            result.label = response["classification"]["label"].as<String>();
            float confidence = response["classification"]["confidence"].as<float>();
            Serial.printf(
                "Classification: %s confidence=%.3f emergency_detected=%s\n",
                result.label.c_str(),
                confidence,
                result.emergencyDetected ? "true" : "false");
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
    Serial.print("Server: ");
    Serial.println(SERVER_BASE_URL);
}

static void setBuzzer(bool enabled) {
    const uint8_t level = (enabled == BUZZER_ACTIVE_HIGH) ? HIGH : LOW;
    digitalWrite(BUZZER_PIN, level);
    Serial.printf(
        "Buzzer GPIO%u: %s (output=%s)\n",
        BUZZER_PIN,
        enabled ? "ON" : "OFF",
        level == HIGH ? "HIGH" : "LOW");
}

static bool isEmergencyLabel(const String &label) {
    String normalized = label;
    normalized.trim();
    normalized.toLowerCase();
    return normalized == "emergency" ||
           normalized == "bahaya" ||
           normalized == "label_1" ||
           normalized == "1";
}

static void triggerEmergencyAlert() {
    Serial.println("EMERGENCY DETECTED: BUZZER DIHIDUPKAN.");
    digitalWrite(LED_PIN, LOW);
    setBuzzer(true);
    delay(3000);
    setBuzzer(false);
    Serial.println("Alarm Emergency selesai: buzzer dimatikan.");
}

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    setBuzzer(false);

    randomSeed(esp_random());
    connectWiFi();
    setupI2SMicrophone();

    Serial.print("Device public key: ");
    Serial.println(schnorrPublicKey(DEVICE_SECRET_KEY));
}

void loop() {
    // LED is reserved for the three-second audio capture window.
    digitalWrite(LED_PIN, LOW);
    Serial.println();
    Serial.println("--- Mulai siklus rekam baru ---");

    SchnorrDeviceProof proof = schnorrCreateCommitment();
    ChallengeResult challenge = requestChallenge(proof.commitment);
    if (!challenge.ok) {
        Serial.println("Challenge failed. Retry in 2 seconds.");
        delay(ERROR_RETRY_DELAY_MS);
        return;
    }

    schnorrCompleteProof(proof, challenge.challenge);

    AuthResult auth = verifyProof(proof.commitment, proof.response);
    if (!auth.ok || auth.token.length() == 0) {
        Serial.println("Authentication failed.");
        delay(ERROR_RETRY_DELAY_MS);
        return;
    }

    ClassificationResult classification = uploadAudioAndGetClassification(auth.token);
    if (!classification.ok) {
        Serial.println("Classification failed. Retry in 2 seconds.");
        delay(ERROR_RETRY_DELAY_MS);
        return;
    }

    bool serverValid = schnorrVerifyServerProof(classification.serverProof);
    Serial.printf("Received label raw: [%s]\n", classification.label.c_str());
    Serial.printf("Server proof valid: %s\n", serverValid ? "yes" : "no");
    const bool emergencyLabel = isEmergencyLabel(classification.label);
    const bool emergencyDetected = classification.emergencyDetected || emergencyLabel;
    Serial.printf("Emergency boolean: %s\n", classification.emergencyDetected ? "true" : "false");
    Serial.printf("Emergency label match: %s\n", emergencyLabel ? "yes" : "no");
    if (emergencyDetected) {
        if (!serverValid) {
            Serial.println("Warning: Emergency label received, but server proof is invalid.");
        }
        triggerEmergencyAlert();
    } else {
        setBuzzer(false);
        Serial.println("Hasil Normal: buzzer tetap mati.");
    }

    Serial.printf("Siklus selesai. Rekam lagi dalam %lu ms.\n", NEXT_CHUNK_DELAY_MS);
    delay(NEXT_CHUNK_DELAY_MS);
}
