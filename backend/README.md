# Backend FastAPI

Backend menangani autentikasi perangkat, penerimaan audio, speech-to-text, koreksi teks, klasifikasi IndoBERT, penyimpanan SQLite, keputusan emergency, server proof, dan monitoring dashboard.

## Struktur

| Folder | Tanggung jawab |
|---|---|
| `api/` | Router, schema request/response, dan dependency injection |
| `auth/` | Token perangkat dan middleware autentikasi |
| `bert/` | Service klasifikasi dan model IndoBERT hasil fine-tuning |
| `config/` | Pembacaan konfigurasi `.env` |
| `database/` | Engine, session, dan database SQLite |
| `models/` | Model tabel SQLAlchemy |
| `repositories/` | Operasi baca/tulis database |
| `services/` | Logika bisnis dan orkestrasi pipeline |
| `speech/` | faster-whisper, preprocessing WAV, dan auto-correct |
| `tests/` | Pengujian otomatis backend |
| `utils/` | Logging, file, exception, dan helper umum |
| `zkp/` | Challenge-response Schnorr dan server proof |

Penjelasan kode lebih rinci tersedia di [`CODE_WALKTHROUGH.md`](CODE_WALKTHROUGH.md).

## Menjalankan

Dari root proyek:

```powershell
.\run_backend_lan.ps1
```

## Endpoint Utama

```text
GET  /api/health
POST /api/devices
POST /api/auth/challenge
POST /api/auth/verify
POST /api/process/audio
GET  /api/monitoring/overview
GET  /api/monitoring/events
GET  /dashboard
```

## Model Aktif

- Speech-to-text: `backend/models/faster-whisper-small`
- Klasifikasi: `backend/bert/trained_model_indobert_full`
- Bahasa: Indonesia (`id`)
- Kelas: `Normal` dan `Emergency`

Nilai sebenarnya dibaca dari `.env`, sehingga model dapat diganti tanpa mengubah source code.

## Pengujian

```powershell
python -m pytest -q
```

Parameter Schnorr dalam proyek masih berukuran kecil dan hanya ditujukan untuk prototype pembelajaran.
