# Secure Voice-Based Emergency Detection System

Sistem ini menggabungkan IoT, Machine Learning, dan Cybersecurity untuk mendeteksi kondisi darurat dari suara pekerja. ESP8266 mengirim audio setelah autentikasi Schnorr Zero-Knowledge Proof. Backend FastAPI menyimpan audio, menjalankan Whisper untuk speech-to-text, mengklasifikasikan transcript dengan BERT, mengirim Telegram jika emergency, lalu mengirim hasil beserta proof server untuk diverifikasi ESP8266.

## Dokumentasi Visual

Tambahkan gambar pendukung di folder `docs/images/` lalu tampilkan di README:

```md
## Dashboard Monitoring
![Dashboard](docs/images/dashboard.png)

## Flowchart Sistem
![Flowchart](docs/images/flowchart.png)

## Prototipe
![Prototype](docs/images/prototype.png)
```

Saran nama file:

- `docs/images/dashboard.png`
- `docs/images/flowchart.png`
- `docs/images/prototype.png`

## Upload ke GitHub

Panduan upload repository yang lebih rapi dan profesional tersedia di:

```text
GITHUB_UPLOAD_GUIDE.md
```

## Struktur Folder

```text
backend/
  api/              Router FastAPI, schema Pydantic, dan dependency injection
  auth/             Challenge-response auth, token, dan middleware
  zkp/              Schnorr parameters, challenge generator, verifier, validator
  speech/           Service OpenAI Whisper
  bert/             Service HuggingFace Transformers + PyTorch
  telegram/         Service Telegram Bot API
  database/         SQLAlchemy engine, session, dan Base
  models/           Model tabel SQLite
  repositories/     Akses data per entitas
  services/         Use case dan orchestration layer
  utils/            Logging, exception handler, helper filesystem
  uploads/          File audio yang diterima
  logs/             Log aplikasi
firmware/esp8266/   Firmware PlatformIO untuk NodeMCU ESP8266
tests/              Unit test pytest
```

## Instalasi

Gunakan Python 3.12.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Whisper membutuhkan `ffmpeg`. Pastikan `ffmpeg` tersedia di PATH.

## Konfigurasi

Edit `.env`:

```text
DATABASE_URL=sqlite:///./backend/database/app.db
UPLOAD_DIR=backend/uploads
LOG_DIR=backend/logs
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EMERGENCY_THRESHOLD=0.8
WHISPER_MODEL_NAME=base
WHISPER_LANGUAGE=
WHISPER_DEVICE=cpu
BERT_MODEL_NAME=bert-base-uncased
BERT_DEVICE=cpu
BERT_EMERGENCY_LABELS=Emergency,EMERGENCY,LABEL_1
BERT_NORMAL_LABELS=Normal,NORMAL,LABEL_0
```

Untuk ESP8266 demo, daftarkan device dengan public key `9` jika `DEVICE_SECRET_KEY=5` di firmware.

## Menjalankan Backend

Panduan langkah demi langkah untuk menjalankan backend, ESP8266, dan troubleshooting tersedia di:

```text
PANDUAN_RUNNING.md
```

```bash
uvicorn backend.main:app --reload
```

Swagger tersedia di:

```text
http://127.0.0.1:8000/docs
```

Endpoint utama:

```text
GET  /api/health
POST /api/devices
POST /challenge
POST /verify
POST /api/process/audio
GET  /dashboard
GET  /api/monitoring/overview
GET  /api/monitoring/events
```

## Menjalankan ESP8266

Versi Arduino IDE tersedia sebagai:

```text
firmware/esp8266/esp8266_emergency_detector.ino
```

1. Buka `firmware/esp8266/include/config.h`.
2. Isi `WIFI_SSID`, `WIFI_PASSWORD`, dan `SERVER_BASE_URL`.
3. Pastikan parameter Schnorr sama dengan backend.
4. Build dan upload dengan PlatformIO:

```bash
cd firmware/esp8266
pio run --target upload
pio device monitor
```

## Penggunaan Whisper

Backend memakai package `openai-whisper`. Model diatur lewat:

```text
WHISPER_MODEL_NAME=base
WHISPER_DEVICE=cpu
WHISPER_LANGUAGE=
```

Gunakan model kecil seperti `tiny` atau `base` untuk laptop biasa. Gunakan `small`, `medium`, atau `large` jika mesin cukup kuat.

## Training Model BERT

Siapkan dataset dua kolom:

```text
text,label
"help fire in area",Emergency
"everything is normal",Normal
```

Fine-tune model dengan HuggingFace `AutoModelForSequenceClassification` untuk dua label. Setelah training, simpan model ke folder lokal, misalnya:

```text
models/bert-emergency
```

Lalu ubah `.env`:

```text
BERT_MODEL_NAME=models/bert-emergency
BERT_EMERGENCY_LABELS=Emergency,EMERGENCY,LABEL_1
BERT_NORMAL_LABELS=Normal,NORMAL,LABEL_0
```

## Pengujian Sistem

Jalankan unit test:

```bash
pytest
```

Test mencakup:

- Schnorr proof verification
- Auth token
- Health endpoint
- OpenAPI/Swagger route availability
- Pipeline ML dengan fake Whisper, fake BERT, dan fake Telegram

## Catatan Produksi

Parameter Schnorr saat ini hanya untuk prototype. Untuk produksi, gunakan parameter kriptografi besar yang direview, secret yang aman, HTTPS, rotasi token, model BERT fine-tuned, dan validasi audio yang lebih ketat.
