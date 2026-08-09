# Peta Kode VoiceGuard-ZKP

Dokumen ini memberi **nama mudah**, fungsi, dan prioritas penjelasan untuk setiap bagian penting proyek. Nama file fisik tidak diubah karena sudah dipakai oleh import Python, konfigurasi model, firmware, dan perintah menjalankan sistem.

## Empat Bagian Besar

| Folder | Nama mudah saat presentasi | Isi utama |
|---|---|---|
| `dataset/` | Bagian Data dan Training | Dataset, preprocessing, fine-tuning, dan evaluasi IndoBERT |
| `backend/` | Bagian Server dan Machine Learning | API, ZKP, Whisper, autocorrect, IndoBERT, database, dan notifikasi |
| `frontend/` | Bagian Perangkat dan Tampilan | Firmware ESP32-S3, dashboard, gambar, dan dokumentasi |
| `output/` | Bagian Hasil Presentasi | File PPTX dan gambar hasil pembuatan materi |

## Urutan Kode yang Ditunjukkan

Jika diminta menunjukkan cara kerja sistem, buka file dengan urutan berikut:

1. `frontend/firmware/esp32_inmp441/...ino` - perangkat merekam dan mengirim audio.
2. `backend/api/v1/auth.py` - perangkat meminta challenge dan membuktikan identitas.
3. `backend/zkp/schnorr.py` - rumus verifikasi Schnorr ZKP.
4. `backend/api/v1/processing.py` - endpoint yang menerima audio.
5. `backend/services/emergency_service.py` - pengendali seluruh pipeline.
6. `backend/speech/service.py` - preprocessing audio dan Whisper.
7. `backend/speech/indonesian_autocorrect.py` - koreksi typo terbatas.
8. `backend/bert/service.py` - klasifikasi Normal atau Emergency.
9. `backend/api/v1/monitoring.py` - dashboard hijau dan merah.
10. `backend/telegram/service.py` - pengiriman notifikasi.

## File Utama di Root

| File | Nama mudah | Fungsi |
|---|---|---|
| `README.md` | Panduan Utama Proyek | Menjelaskan arsitektur, instalasi, cara menjalankan, dan batasan sistem |
| `PETA_KODE_PROYEK.md` | Peta Penjelasan Kode | Membantu mencari dan menjelaskan setiap bagian kode |
| `requirements.txt` | Daftar Kebutuhan Utama | Mengarahkan instalasi dependency backend |
| `pytest.ini` | Konfigurasi Pengujian | Mengatur lokasi dan perilaku pytest |
| `run_backend_lan.bat` | Menjalankan Server lewat CMD | Menyalakan FastAPI pada jaringan lokal Windows |
| `run_backend_lan.ps1` | Menjalankan Server lewat PowerShell | Versi PowerShell untuk menyalakan FastAPI |
| `.env` | Konfigurasi Rahasia | Menyimpan path model, database, token Telegram, dan konfigurasi lokal; jangan ditampilkan penuh |
| `.env.example` | Contoh Konfigurasi | Contoh variabel yang harus diisi tanpa membagikan rahasia |

## Folder `dataset/` - Data dan Training

| File | Nama mudah | Fungsi |
|---|---|---|
| `dataset.csv` | Dataset Awal | Contoh data awal dan tambahan sebelum penggabungan |
| `dataset_final.csv` | Dataset Final | Data 54.656 baris untuk kelas Normal dan Emergency |
| `train_bert_final_dataset.ipynb` | Notebook Training Utama | Preprocessing, pembagian data, fine-tuning IndoBERT, dan evaluasi |
| `run_full_finetune_indobert.py` | Runner Training | Menjalankan seluruh notebook secara otomatis |
| `run_full_finetune_indobert.bat` | Tombol Training Windows | Menjalankan runner melalui Command Prompt |
| `README.md` | Panduan Dataset | Menjelaskan sumber data dan alur pengolahan |
| `*.log` | Catatan Proses Training | Menyimpan keluaran, status, dan kesalahan training |

## Folder `backend/` - Server Utama

| File/folder | Nama mudah | Fungsi |
|---|---|---|
| `main.py` | Pintu Masuk Server | Membuat aplikasi FastAPI dan menghubungkan seluruh modul |
| `requirements.txt` | Dependency Backend | Daftar library Python khusus backend |
| `README.md` | Panduan Backend | Cara menjalankan, endpoint, dan model aktif |
| `CODE_WALKTHROUGH.md` | Panduan Membaca Backend | Menjelaskan alur kode backend secara bertahap |

### `backend/api/` - Pintu Komunikasi Sistem

| File | Nama mudah | Fungsi |
|---|---|---|
| `routes.py` | Penggabung Endpoint | Menggabungkan seluruh endpoint API versi 1 |
| `dependencies.py` | Penyedia Komponen | Menyediakan database, repository, dan service kepada endpoint |
| `schemas.py` | Format Data API | Menentukan bentuk request dan response menggunakan Pydantic |
| `v1/auth.py` | Endpoint Autentikasi ZKP | Menerima commitment, membuat challenge, dan memverifikasi proof |
| `v1/devices.py` | Endpoint Perangkat | Mendaftarkan dan membaca identitas serta lokasi perangkat |
| `v1/processing.py` | Endpoint Proses Audio | Menerima upload audio dan memulai pipeline deteksi |
| `v1/monitoring.py` | Endpoint dan Tampilan Dashboard | Menyediakan data monitoring serta HTML dashboard |
| `v1/health.py` | Pemeriksaan Server | Menunjukkan apakah backend sedang aktif |
| `__init__.py` | Penanda Package | Menjadikan folder dapat diimpor sebagai modul Python |

### `backend/auth/` - Token Akses Perangkat

| File | Nama mudah | Fungsi |
|---|---|---|
| `service.py` | Pengelola Autentikasi | Menghubungkan perangkat, challenge ZKP, verifikasi, dan token |
| `tokens.py` | Pembuat Token | Membuat dan memeriksa token sementara untuk perangkat valid |
| `middleware.py` | Penjaga Endpoint | Menolak request perangkat yang tidak memiliki token valid |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/zkp/` - Schnorr Zero-Knowledge Proof

| File | Nama mudah | Fungsi |
|---|---|---|
| `params.py` | Parameter Matematika ZKP | Menyimpan nilai prototype `p`, `q`, dan `g` |
| `challenge.py` | Pembuat Tantangan | Membuat nilai challenge acak untuk setiap autentikasi |
| `schnorr.py` | Perhitungan Schnorr | Mendefinisikan proof dan memeriksa persamaan Schnorr |
| `validator.py` | Pemeriksa Format Proof | Memastikan commitment, challenge, dan response valid |
| `service.py` | Layanan ZKP | Menyediakan fungsi ZKP kepada lapisan autentikasi |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/speech/` - Audio dan Whisper

| File | Nama mudah | Fungsi |
|---|---|---|
| `service.py` | Mesin Speech-to-Text | Menyaring audio, menormalisasi volume, dan menjalankan faster-whisper Small |
| `indonesian_autocorrect.py` | Korektor Typo Darurat | Memperbaiki kesalahan transkripsi yang sudah ditinjau |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/bert/` - Klasifikasi Teks

| File/folder | Nama mudah | Fungsi |
|---|---|---|
| `service.py` | Mesin Klasifikasi IndoBERT | Tokenisasi, inferensi, softmax, label, dan confidence |
| `trained_model_indobert_full/` | Model IndoBERT Aktif | Model hasil fine-tuning dataset proyek |
| `trained_model/` | Model Eksperimen Lama | Model sebelumnya yang disimpan sebagai referensi |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

Isi folder model seperti `config.json`, `model.safetensors`, dan `tokenizer.json` merupakan hasil training. File tersebut tidak perlu dijelaskan baris per baris.

### `backend/services/` - Logika Utama Sistem

| File | Nama mudah | Fungsi |
|---|---|---|
| `emergency_service.py` | Pengendali Pipeline Darurat | Menghubungkan audio, Whisper, autocorrect, IndoBERT, keputusan, notifikasi, dan server proof |
| `audio_service.py` | Pengelola Audio | Memvalidasi format upload dan menyimpan file WAV |
| `classification_service.py` | Pengelola Hasil Klasifikasi | Menyimpan hasil Normal/Emergency beserta confidence |
| `device_service.py` | Pengelola Perangkat | Mengatur perangkat terdaftar, public key, dan lokasi |
| `monitoring_service.py` | Penyusun Data Dashboard | Mengambil dan merapikan data monitoring |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/models/` - Bentuk Tabel Database

| File | Nama mudah | Fungsi |
|---|---|---|
| `device.py` | Tabel Perangkat | ID, nama, public key, lokasi, dan status perangkat |
| `authentication_challenge.py` | Tabel Challenge | Menyimpan challenge ZKP dan masa berlakunya |
| `authentication_log.py` | Tabel Riwayat Autentikasi | Mencatat autentikasi berhasil atau gagal |
| `audio_record.py` | Tabel Rekaman Audio | Menyimpan metadata file audio |
| `transcript.py` | Tabel Hasil Whisper | Menyimpan teks hasil transkripsi |
| `classification.py` | Tabel Hasil IndoBERT | Menyimpan label dan confidence |
| `notification.py` | Tabel Notifikasi | Menyimpan status pengiriman peringatan |
| `all_models.py` | Penggabung Model Tabel | Memastikan seluruh tabel didaftarkan ke SQLAlchemy |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/repositories/` - Operasi Database

| File | Nama mudah | Fungsi |
|---|---|---|
| `device_repository.py` | Query Perangkat | Membaca dan menyimpan perangkat |
| `challenge_repository.py` | Query Challenge | Membuat dan mengambil challenge ZKP |
| `auth_repository.py` | Query Autentikasi | Menyimpan riwayat autentikasi |
| `audio_repository.py` | Query Audio | Menyimpan metadata audio |
| `transcript_repository.py` | Query Transkrip | Menyimpan hasil Whisper |
| `classification_repository.py` | Query Klasifikasi | Menyimpan hasil IndoBERT |
| `notification_repository.py` | Query Notifikasi | Menyimpan hasil pengiriman notifikasi |
| `monitoring_repository.py` | Query Dashboard | Mengambil ringkasan dan event terbaru |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/database/` - Koneksi Database

| File | Nama mudah | Fungsi |
|---|---|---|
| `base.py` | Dasar Model Database | Menyediakan Base dan kolom waktu bersama |
| `session.py` | Koneksi SQLite | Membuat engine dan session database |
| `app.db` | Database Runtime | Menyimpan data perangkat, audio, transkrip, dan klasifikasi |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/telegram/` - Notifikasi

| File | Nama mudah | Fungsi |
|---|---|---|
| `service.py` | Pengirim Peringatan Telegram | Mengirim pesan darurat dan mencatat statusnya |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/config/` dan `backend/utils/` - Konfigurasi dan Bantuan

| File | Nama mudah | Fungsi |
|---|---|---|
| `config/settings.py` | Pusat Konfigurasi | Membaca `.env`, path model, threshold, dan pengaturan server |
| `utils/files.py` | Bantuan File | Operasi file umum |
| `utils/logging.py` | Pengaturan Log | Menentukan format dan lokasi catatan sistem |
| `utils/exceptions.py` | Daftar Kesalahan | Mendefinisikan exception khusus aplikasi |
| `utils/exception_handlers.py` | Penanganan Kesalahan API | Mengubah exception menjadi response yang jelas |
| `__init__.py` | Penanda Package | Menjadikan folder sebagai modul Python |

### `backend/tests/` - Bukti Pengujian

| File | Nama mudah | Fungsi |
|---|---|---|
| `test_zkp.py` | Tes Schnorr ZKP | Memeriksa proof valid dan tidak valid |
| `test_tokens.py` | Tes Token Perangkat | Memeriksa pembuatan dan validasi token |
| `test_api.py` | Tes Endpoint | Memeriksa komunikasi API utama |
| `test_indonesian_autocorrect.py` | Tes Koreksi Typo | Memeriksa pasangan typo dan mencegah koreksi palsu |
| `test_speech_audio_preprocessing.py` | Tes Kualitas Audio | Memeriksa penolakan audio kosong atau terlalu lemah |
| `test_emergency_pipeline.py` | Tes Pipeline Menyeluruh | Memeriksa alur Whisper sampai penyimpanan keputusan |
| `test_emergency_keyword_override.py` | Tes Aturan Kata Darurat | Memeriksa aturan tambahan untuk ucapan darurat |

### Folder Runtime dan Model Besar

| Folder | Nama mudah | Catatan |
|---|---|---|
| `backend/models/faster-whisper-small/` | Model Whisper Small | Model OpenAI Whisper dalam format CTranslate2; jangan dibuka baris per baris |
| `backend/uploads/` | Rekaman Masuk | File audio runtime dari perangkat |
| `backend/logs/` | Catatan Server | Log aktivitas dan error backend |
| `backend/__pycache__/` | Cache Python | Dibuat otomatis dan tidak perlu dijelaskan |

## Folder `frontend/` - Perangkat dan Tampilan

### Firmware Aktif

| File | Nama mudah | Fungsi |
|---|---|---|
| `frontend/firmware/esp32_inmp441/...ino` | Program Utama ESP32-S3 | Wi-Fi, INMP441, rekaman 3 detik, ZKP, upload, LED, dan buzzer |
| `frontend/firmware/esp32_inmp441/README.md` | Panduan Perangkat Aktif | Pin, cara upload, dan mekanisme firmware |

### Firmware Lama

| File | Nama mudah | Fungsi |
|---|---|---|
| `frontend/firmware/esp8266/src/main.cpp` | Program Utama ESP8266 Lama | Alur perangkat analog versi sebelumnya |
| `frontend/firmware/esp8266/src/api_client.cpp` | Komunikasi API Lama | Mengirim request dari ESP8266 |
| `frontend/firmware/esp8266/src/schnorr.cpp` | Perhitungan ZKP Lama | Implementasi Schnorr pada ESP8266 |
| `frontend/firmware/esp8266/include/config.h` | Konfigurasi Firmware Lama | Wi-Fi, server, pin, dan identitas perangkat |
| `frontend/firmware/esp8266/include/api_client.h` | Deklarasi API Client | Header untuk komunikasi API |
| `frontend/firmware/esp8266/include/schnorr.h` | Deklarasi Schnorr | Header fungsi ZKP |
| `frontend/firmware/esp8266/platformio.ini` | Konfigurasi PlatformIO | Board, framework, dan library firmware lama |
| `frontend/firmware/esp8266/...ino` | Sketch Referensi Lama | Versi Arduino dari prototype ESP8266 |

Firmware ESP8266 hanya referensi sejarah. Saat demonstrasi gunakan ESP32-S3 dan INMP441.

### Dokumentasi Visual

| Folder/file | Nama mudah | Fungsi |
|---|---|---|
| `frontend/docs/images/` | Gambar Proyek | Dashboard, flowchart, dan foto prototype |
| `frontend/docs/guides/running-project.md` | Panduan Menjalankan | Langkah menghidupkan proyek |
| `frontend/docs/guides/upload-github.md` | Panduan GitHub | Langkah mengunggah proyek |
| `frontend/docs/video_storyboard/` | Materi Video Animasi | Character sheet, sebelas keyframe, subtitle, dan panduan produksi |
| `frontend/docs/README.md` | Indeks Dokumentasi | Menjelaskan isi folder dokumentasi |
| `README.md` | Panduan Frontend | Menjelaskan dashboard dan firmware aktif |

## Jawaban Singkat Saat Ditanya Penguji

**“Di mana kode utama sistem?”**

> Kode perangkat berada pada firmware ESP32-S3, sedangkan pusat prosesnya berada pada `backend/services/emergency_service.py`.

**“Di mana machine learning dijalankan?”**

> Whisper dijalankan pada `backend/speech/service.py`, autocorrect pada `backend/speech/indonesian_autocorrect.py`, dan IndoBERT pada `backend/bert/service.py`.

**“Di mana ZKP diterapkan?”**

> Perhitungan Schnorr berada pada `backend/zkp/schnorr.py`, sedangkan alur challenge dan verifikasinya masuk melalui `backend/api/v1/auth.py`.

**“Di mana hasil ditampilkan?”**

> Dashboard dan endpoint monitoring berada pada `backend/api/v1/monitoring.py`.

## File yang Tidak Perlu Dibuka Saat Presentasi

- `model.safetensors`, `model.bin`, dan file tokenizer karena merupakan hasil model biner.
- `app.db` karena merupakan database runtime.
- `__pycache__`, `.pyc`, log, dan file upload karena dibuat otomatis.
- Semua `__init__.py` kecuali penguji menanyakan struktur package Python.
