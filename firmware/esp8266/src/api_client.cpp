#include "api_client.h"

#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

#include "config.h"

static bool parseJson(const String &payload, JsonDocument &doc) {
    DeserializationError error = deserializeJson(doc, payload);
    if (error) {
        Serial.print("JSON parse failed: ");
        Serial.println(error.c_str());
        return false;
    }
    return true;
}

static void printHttpFailure(const char *action, int code) {
    Serial.print(action);
    Serial.print(" failed: ");
    Serial.print(code);
    if (code < 0) {
        Serial.print(" (");
        Serial.print(HTTPClient::errorToString(code));
        Serial.print(")");
    }
    Serial.println();
}

ChallengeResult requestChallenge(uint32_t commitment) {
    WiFiClient client;
    HTTPClient http;
    ChallengeResult result = {false, 0};

    String url = String(SERVER_BASE_URL) + "/challenge";
    Serial.print("POST ");
    Serial.println(url);
    http.begin(client, url);
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
        printHttpFailure("Challenge request", code);
    }

    http.end();
    return result;
}

AuthResult verifyProof(uint32_t commitment, uint32_t responseValue) {
    WiFiClient client;
    HTTPClient http;
    AuthResult result = {false, ""};

    String url = String(SERVER_BASE_URL) + "/verify";
    Serial.print("POST ");
    Serial.println(url);
    http.begin(client, url);
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
        printHttpFailure("Verify request", code);
    }

    http.end();
    return result;
}

ClassificationResult uploadAudioAndGetClassification(const String &authToken) {
    WiFiClient client;
    HTTPClient http;
    ClassificationResult result;
    result.ok = false;

    String url = String(SERVER_BASE_URL) + "/api/process/audio";
    Serial.print("POST ");
    Serial.println(url);
    http.begin(client, url);
    http.addHeader("X-Auth-Token", authToken);
    http.addHeader("Content-Type", "multipart/form-data; boundary=----esp8266boundary");

    // Replace this placeholder with bytes captured from MAX4466.
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
        printHttpFailure("Audio upload", code);
    }

    http.end();
    return result;
}
