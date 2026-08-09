# Panduan Menjelaskan Kode Backend

Dokumen ini membantu menjelaskan kode tanpa memenuhi setiap baris dengan komentar yang berulang.

## Titik Masuk

`backend/main.py` membuat aplikasi FastAPI, memasang middleware token, mendaftarkan exception handler, menyambungkan router, dan menjalankan proses startup. Saat `PRELOAD_ML_MODELS=true`, Whisper dan IndoBERT dimuat lebih awal agar request pertama tidak lambat.

## API

- `backend/api/routes.py`: menggabungkan semua router versi API.
- `backend/api/dependencies.py`: membuat dan membagikan service/repository.
- `backend/api/schemas.py`: mendefinisikan bentuk request dan response Pydantic.
- `backend/api/v1/auth.py`: challenge dan verifikasi Schnorr.
- `backend/api/v1/devices.py`: registrasi serta pembacaan perangkat.
- `backend/api/v1/processing.py`: endpoint upload audio end-to-end.
- `backend/api/v1/monitoring.py`: endpoint data monitoring dan HTML dashboard.

## Lapisan Service

- `audio_service.py`: memvalidasi upload dan menyimpan audio.
- `emergency_service.py`: mengorkestrasi Whisper, koreksi, BERT, aturan threshold, notifikasi, dan server proof.
- `classification_service.py`: menyimpan hasil klasifikasi.
- `device_service.py`: mengelola perangkat terdaftar.
- `monitoring_service.py`: menyusun data yang dibutuhkan dashboard.

## Machine Learning

`backend/speech/service.py` menjalankan urutan berikut:

1. Membaca WAV mono 16-bit.
2. Mengurangi DC offset dan noise di luar pita utama suara.
3. Mengukur aktivitas suara agar keheningan tidak ditranskripsikan.
4. Menormalisasi volume secara terbatas.
5. Menjalankan faster-whisper dengan bahasa `id`.
6. Menolak hasil yang terlalu berulang atau menyerupai halusinasi.

`backend/speech/indonesian_autocorrect.py` hanya mengoreksi kata yang cukup dekat dengan kosakata penting. Aturan ini dibatasi agar teks normal tidak berubah secara agresif.

`backend/bert/service.py` melakukan tokenisasi, inferensi IndoBERT, softmax, pemetaan label, dan pengembalian confidence.

## ZKP

`backend/zkp/` berisi implementasi Schnorr prototype:

```text
commitment t = g^r mod p
response   s = r + c*x mod q
verifikasi g^s = t * y^c mod p
```

Secret key `x` tidak dikirim ke backend. Parameter kecil saat ini hanya untuk demonstrasi akademik.

## Database

- `backend/models/`: tabel SQLAlchemy.
- `backend/repositories/`: query database tanpa logika bisnis.
- `backend/database/session.py`: engine dan session SQLite.
- `backend/database/app.db`: database lokal runtime.

## Urutan Request Audio

```text
processing.py
  -> AuthenticationMiddleware
  -> EmergencyService
  -> AudioService
  -> SpeechToTextService
  -> IndonesianTextCorrector
  -> TextClassificationService
  -> ClassificationRepository
  -> server proof
  -> response ESP32-S3
```

## Komentar yang Dipakai

- Docstring menjelaskan tujuan class dan function.
- Komentar sebelum blok menjelaskan alasan teknis atau aturan yang tidak langsung terlihat.
- Nama function dan variabel menjelaskan operasi sederhana.
- Komentar tidak ditambahkan pada setiap assignment karena akan mengulang kode dan memperbesar risiko dokumentasi tidak lagi sesuai implementasi.
