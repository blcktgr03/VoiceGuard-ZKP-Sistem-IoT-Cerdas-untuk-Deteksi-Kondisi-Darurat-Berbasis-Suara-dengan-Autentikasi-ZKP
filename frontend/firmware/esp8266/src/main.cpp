#include <Arduino.h>
#include <ESP8266WiFi.h>

#include "api_client.h"
#include "config.h"
#include "schnorr.h"

static void connectWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.print("SSID: ");
    Serial.println(WIFI_SSID);
    Serial.print("Connected: ");
    Serial.println(WiFi.localIP());
    Serial.print("Gateway: ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("Server: ");
    Serial.println(SERVER_BASE_URL);
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
