#pragma once

#include <Arduino.h>

static const char *WIFI_SSID = "YOUR_WIFI_SSID";
static const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
static const char *SERVER_BASE_URL = "http://192.168.93.132:8000";

static const char *DEVICE_ID = "esp8266-worker-01";

// Demo Schnorr parameters must match backend/zkp/params.py.
// Use reviewed large parameters and a big integer library for production.
static const uint32_t SCHNORR_P = 23;
static const uint32_t SCHNORR_Q = 11;
static const uint32_t SCHNORR_G = 2;

static const uint32_t DEVICE_SECRET_KEY = 5;
static const uint32_t SERVER_PUBLIC_KEY = 13;

static const uint8_t BUZZER_PIN = D5;
