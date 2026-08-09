# Panduan Singkat Menjalankan Proyek

Panduan lengkap tersedia di [`../../../README.md`](../../../README.md).

## Backend

Dari root proyek:

```powershell
.\run_backend_lan.ps1
```

atau:

```powershell
& "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Perangkat Utama

Buka dan upload firmware berikut menggunakan Arduino IDE:

```text
frontend/firmware/esp32_inmp441/esp32_inmp441_emergency_detector/esp32_inmp441_emergency_detector.ino
```

Salin `config.example.h` menjadi `config.h` di folder sketch dan isi konfigurasi jaringan sebelum compile. File lokal tersebut tidak dilacak Git.

Periksa sebelum upload:

1. SSID dan password Wi-Fi.
2. IP laptop pada `SERVER_BASE_URL`.
3. Pin INMP441: SD 16, WS 17, SCK 18.
4. LED GPIO 12 dan buzzer GPIO 9.

Folder `frontend/firmware/esp8266` adalah implementasi analog lama dan hanya dipertahankan sebagai referensi.

## Dashboard

```text
http://localhost:8000/dashboard
```
