# Secure Voice-Based Emergency Detection Backend

Backend FastAPI untuk sistem deteksi darurat berbasis suara. Versi ini berfokus pada fondasi Clean Architecture: konfigurasi, database, model, repository, service, router, dependency injection, upload audio, dan logging.

Whisper, BERT, Telegram delivery, dan Schnorr ZKP sudah tersedia untuk flow prototype.

## Menjalankan

```bash
copy backend\.env.example .env
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Endpoint health check:

```text
GET /api/health
```

## Machine Learning Pipeline

Pipeline `POST /api/process/audio`:

1. Server menerima audio dari ESP8266.
2. Audio disimpan ke `backend/uploads`.
3. Metadata audio disimpan ke SQLite.
4. Whisper mengubah audio menjadi teks.
5. Transcript disimpan ke tabel `transcripts`.
6. BERT mengklasifikasikan teks.
7. Classification disimpan ke tabel `classifications`.
8. Jika label `Emergency` dan confidence `>= EMERGENCY_THRESHOLD`, server mengirim Telegram.
9. Response ke ESP8266 berisi hasil klasifikasi dan `server_proof`.

Konfigurasi model ada di `.env`:

```text
WHISPER_MODEL_NAME=base
WHISPER_LANGUAGE=
WHISPER_DEVICE=cpu
BERT_MODEL_NAME=bert-base-uncased
BERT_DEVICE=cpu
BERT_EMERGENCY_LABELS=Emergency,EMERGENCY,LABEL_1
BERT_NORMAL_LABELS=Normal,NORMAL,LABEL_0
EMERGENCY_THRESHOLD=0.8
```

Untuk hasil klasifikasi yang benar, gunakan model BERT yang sudah fine-tuned untuk dua kelas `Emergency` dan `Normal`, lalu sesuaikan `BERT_EMERGENCY_LABELS` dan `BERT_NORMAL_LABELS`.

## Schnorr Authentication Flow

Versi ini memakai parameter demo yang sama dengan firmware:

```text
p = 23
q = 11
g = 2
```

Untuk prototype ESP8266, `DEVICE_SECRET_KEY = 5`, sehingga public key device adalah:

```text
y = g^x mod p = 2^5 mod 23 = 9
```

Daftarkan device dengan `public_key` bernilai `"9"` sebelum autentikasi.

1. ESP8266 membuat nonce `r` dan commitment `t = g^r mod p`.
2. ESP8266 memanggil `POST /challenge` dengan `device_id` dan `commitment`.
3. Server membuat challenge acak `c`, menyimpannya sementara, lalu mengirimkannya ke ESP8266.
4. ESP8266 menghitung response `s = r + c*x mod q`.
5. ESP8266 memanggil `POST /verify` dengan `device_id`, `commitment`, dan `response`.
6. Server memverifikasi `g^s == t * y^c mod p`.
7. Jika valid, server mengirim `auth_token`.
8. Upload audio ke `POST /api/process/audio` wajib membawa header `X-Auth-Token`.
9. Setelah klasifikasi, response membawa `server_proof` agar ESP8266 bisa memverifikasi bahwa hasil berasal dari server resmi.

Endpoint utama:

```text
POST /challenge
POST /verify
POST /api/process/audio
GET  /dashboard
GET  /api/monitoring/overview
GET  /api/monitoring/events
```

Endpoint challenge dan verify juga tersedia sebagai:

```text
POST /api/auth/challenge
POST /api/auth/verify
```

Catatan: parameter Schnorr saat ini hanya untuk demo dan pembelajaran. Untuk produksi, ganti dengan parameter besar yang direview dan gunakan library big integer di firmware.
