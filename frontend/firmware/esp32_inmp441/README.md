# ESP32-S3 + INMP441 Firmware

Firmware ini dipakai untuk mengganti MAX4466 analog dengan mikrofon digital INMP441 berbasis I2S.

## Pinout INMP441 ke ESP32-S3

| INMP441 | ESP32-S3 | Keterangan |
|---|---:|---|
| VDD | 3V3 | Wajib 3.3V, jangan 5V |
| GND | GND | Ground |
| SCK / BCLK | GPIO18 | I2S bit clock |
| WS / LRCL | GPIO17 | I2S word select |
| SD / DOUT | GPIO16 | Data audio dari mic |
| L/R | GND | Channel kiri, sesuai `I2S_CHANNEL_FMT_ONLY_LEFT` |

Pin tambahan:

| Komponen | ESP32-S3 | Keterangan |
|---|---:|---|
| LED | GPIO12 | Menyala hanya saat merekam/streaming audio |
| Buzzer | GPIO9 | Buzzer aktif hanya saat Emergency |

Pasang buzzer pada pin alarm berikut:

- pin sinyal/positif buzzer -> GPIO9
- pin negatif buzzer -> GND

LED GPIO12 menyala hanya selama INMP441 merekam dan men-stream chunk audio 3 detik. Setelah rekaman selesai, LED mati selama backend menjalankan Whisper dan BERT. Setelah hasil diterima, perangkat memulai siklus berikutnya dengan jeda minimum 10 ms untuk menjaga tugas Wi-Fi ESP32 tetap stabil. Jika hasilnya `Emergency`, buzzer menyala selama 3 detik; pada hasil `Normal`, buzzer tetap mati.

Sebelum LED rekam menyala, firmware membersihkan buffer I2S lama selama 60 ms. Saat LED mulai menyala, seluruh awal ucapan langsung masuk ke chunk sehingga suku kata pertama tidak terpotong.

Jika modul buzzer merupakan tipe aktif-LOW, ubah:

```cpp
static const bool BUZZER_ACTIVE_HIGH = true;
```

menjadi `false`.

## Konfigurasi yang Perlu Dicek

Salin `config.example.h` menjadi `config.h` di folder sketch, lalu isi konfigurasi jaringan lokal:

```cpp
static const char *WIFI_SSID = "YOUR_WIFI_SSID";
static const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
static const char *SERVER_BASE_URL = "http://YOUR_SERVER_IP:8000";
```

Pastikan `SERVER_BASE_URL` sesuai IP laptop yang menjalankan backend. File `config.h` diabaikan Git agar kredensial tidak ikut terunggah.

## Konfigurasi Audio

Firmware memakai:

```cpp
AUDIO_SAMPLE_RATE_HZ = 16000;
AUDIO_CHUNK_DURATION_MS = 3000;
```

Artinya ESP32-S3 merekam audio 3 detik pada 16 kHz, lalu mengirim WAV 16-bit mono ke backend.
Format ini lebih cocok untuk Whisper dibanding MAX4466 analog.

## Arduino IDE

Library yang dibutuhkan:

- ArduinoJson
- ESP32 board package

Board yang umum dipakai:

```text
ESP32S3 Dev Module
```

Upload file:

```text
frontend/firmware/esp32_inmp441/esp32_inmp441_emergency_detector/esp32_inmp441_emergency_detector.ino
```

## Backend

Backend tetap sama. Jalankan:

```powershell
# Jalankan dari root proyek machine_learning.
& "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Device masih memakai:

```json
{
  "device_id": "esp32s3-inmp441-worker-01",
  "name": "ESP32-S3 INMP441 Worker 01",
  "public_key": "9",
  "location": "Ruang 1"
}
```

Kalau sebelumnya hanya device lama yang terdaftar, daftarkan device ESP32-S3 ini juga melalui endpoint `POST /api/devices`.

## Tanda Berhasil di Serial Monitor

Saat berjalan normal, Serial Monitor akan menampilkan:

```text
INMP441 I2S microphone ready.
--- Mulai siklus rekam baru ---
=== BICARA SEKARANG ===
Streamed 64000 samples @ 16000 Hz, PCM16 min=... max=... avgAbs=... active=...%
Classification: Normal/Emergency confidence=...
Server proof valid: yes
```

Jika `PCM16 min` dan `PCM16 max` terlalu dekat dengan 0, suara masih terlalu kecil.
Jika sering mentok di sekitar `-32768` atau `32767`, audio terlalu besar/clipping.
