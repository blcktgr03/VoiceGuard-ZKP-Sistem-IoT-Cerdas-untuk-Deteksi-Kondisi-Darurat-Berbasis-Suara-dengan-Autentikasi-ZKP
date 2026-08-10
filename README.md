
# VoiceGuard ZKP

Proyek ini mendeteksi ucapan darurat pekerja menggunakan perangkat ESP32-S3 dan mikrofon INMP441. Audio dikirim ke FastAPI setelah perangkat lolos autentikasi Schnorr Zero-Knowledge Proof (ZKP), diubah menjadi teks bahasa Indonesia oleh faster-whisper, dikoreksi, lalu diklasifikasikan sebagai `Normal` atau `Emergency` oleh IndoBERT. Hasil akhirnya ditampilkan pada dashboard monitoring dan dikirim kembali ke perangkat untuk mengendalikan buzzer.

## Tiga Bagian Utama

```text
machine_learning/
|-- dataset/                 Data final, notebook, dan runner fine-tuning
|-- backend/                 FastAPI, ZKP, Whisper, IndoBERT, database, dan tests
|-- frontend/                Firmware perangkat, materi UI, dan dokumentasi visual
|-- .env                     Konfigurasi lokal dan rahasia, tidak masuk Git
|-- .env.example             Contoh konfigurasi
|-- requirements.txt         Pintu instalasi dependensi backend
|-- run_backend_lan.bat      Menjalankan server dari Command Prompt
|-- run_backend_lan.ps1      Menjalankan server dari PowerShell
`-- README.md                Dokumentasi utama proyek
```

Folder `tmp/`, `output/`, cache, database, log, upload audio, konfigurasi perangkat lokal, dan bobot model berukuran besar tetap disimpan lokal tetapi tidak dimasukkan ke Git.

Struktur rinci tersedia pada:

- [`PETA_KODE_PROYEK.md`](PETA_KODE_PROYEK.md) - nama mudah dan fungsi setiap folder/file untuk demonstrasi kode
- [`dataset/README.md`](dataset/README.md)
- [`backend/README.md`](backend/README.md)
- [`backend/CODE_WALKTHROUGH.md`](backend/CODE_WALKTHROUGH.md)
- [`frontend/README.md`](frontend/README.md)

## Arsitektur Sistem

```text
Suara pekerja
    |
    v
INMP441 -> ESP32-S3 -> Schnorr ZKP -> FastAPI
                                      |
                                      v
                              Penyimpanan audio WAV
                                      |
                                      v
                           faster-whisper bahasa Indonesia
                                      |
                                      v
                              Koreksi teks terbatas
                                      |
                                      v
                            IndoBERT Normal/Emergency
                                |                 |
                                v                 v
                         Dashboard hijau     Dashboard merah
                                                  |
                                                  v
                                         Buzzer pada ESP32-S3
```

## Mekanisme Utama

1. ESP32-S3 terhubung ke Wi-Fi dan membaca audio digital dari INMP441.
2. Perangkat meminta challenge ZKP menggunakan ID dan commitment.
3. Backend memverifikasi proof tanpa menerima secret key perangkat.
4. Perangkat yang valid memperoleh token autentikasi sementara.
5. Audio direkam dalam chunk tiga detik dan dikirim sebagai WAV 16 kHz mono.
6. Backend menolak audio yang tidak memiliki aktivitas suara memadai.
7. faster-whisper mentranskripsikan audio dengan bahasa Indonesia.
8. Auto-correct memperbaiki kata yang dekat dengan kosakata penting secara terbatas.
9. IndoBERT memberi label `Normal` atau `Emergency` beserta confidence.
10. Aturan deteksi memakai confidence tinggi satu chunk atau dua chunk berurutan.
11. Dashboard membaca event terbaru setiap satu detik dan mengganti keadaan visual.
12. Backend mengirim hasil dan server proof ke ESP32-S3.
13. Buzzer menyala hanya saat keputusan akhir adalah emergency.

## Perangkat Keras Utama

| Komponen | Fungsi | Pin ESP32-S3 |
|---|---|---|
| INMP441 SD | Data audio I2S | GPIO 16 |
| INMP441 WS | Word select/LRCL | GPIO 17 |
| INMP441 SCK | Bit clock I2S | GPIO 18 |
| INMP441 VDD | Catu daya | 3V3 |
| INMP441 GND | Ground | GND |
| INMP441 L/R | Kanal kiri | GND |
| LED | Indikator perekaman | GPIO 12 |
| Buzzer | Alarm emergency | GPIO 9 |

Firmware aktif berada di:

```text
frontend/firmware/esp32_inmp441/esp32_inmp441_emergency_detector/
```

## Persiapan Backend

Jalankan perintah berikut dari root proyek (Python 3.11 atau 3.12 direkomendasikan).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Pastikan `.env` minimal menunjuk ke aset lokal berikut:

```env
DATABASE_URL=sqlite:///./backend/database/app.db
UPLOAD_DIR=backend/uploads
LOG_DIR=backend/logs
WHISPER_ENGINE=faster-whisper
WHISPER_MODEL_PATH=backend/models/faster-whisper-small
WHISPER_LANGUAGE=id
BERT_MODEL_NAME=backend/bert/trained_model_indobert_full
```

Jangan membagikan `.env` karena dapat berisi password Wi-Fi, token, atau secret aplikasi.

### Menyiapkan Model ML

Bobot model lokal tidak dilacak oleh Git karena setiap file berukuran sekitar 418-475 MB, melebihi batas file biasa GitHub. Struktur dan metadata model tetap dipertahankan. Pada komputer baru:

1. Letakkan model IndoBERT hasil fine-tuning di `backend/bert/trained_model_indobert_full/`.
2. Letakkan model CTranslate2 Whisper di `backend/models/faster-whisper-small/`, atau kosongkan `WHISPER_MODEL_PATH` agar faster-whisper mengunduh model bernama `WHISPER_MODEL_NAME` saat pertama dijalankan.
3. Pastikan `BERT_MODEL_NAME` dan `WHISPER_MODEL_PATH` di `.env` menunjuk ke lokasi tersebut.

Jika bobot perlu dibagikan bersama proyek, gunakan Git LFS atau GitHub Release, bukan commit Git biasa.

## Menjalankan Backend

```powershell
.\run_backend_lan.ps1
```

Alternatif dari Command Prompt adalah `run_backend_lan.bat`. Kedua launcher memakai environment pengembangan lokal yang sudah ada, lalu `.venv`, lalu Python dari `PATH`. Variabel `VOICEGUARD_PYTHON` dapat digunakan untuk memilih executable Python secara eksplisit.

Alamat yang digunakan:

| Layanan | Alamat |
|---|---|
| Dashboard | `http://localhost:8000/dashboard` |
| Dokumentasi API | `http://localhost:8000/docs` |
| Health check | `http://localhost:8000/api/health` |
| Backend untuk ESP32 | `http://IP-LAPTOP:8000` |

Cari IP laptop dengan:

```powershell
ipconfig
```

Gunakan nilai IPv4 Wi-Fi pada `SERVER_BASE_URL` di firmware. ESP32-S3 dan laptop harus berada pada jaringan yang sama.

## Registrasi Perangkat

Prototype Schnorr memakai parameter demo `p=23`, `q=11`, dan `g=2`. Secret perangkat `x=5` menghasilkan public key perangkat `y=9`, sedangkan public key server untuk server proof adalah `13`. Daftarkan perangkat satu kali melalui Swagger atau request berikut:

```powershell
$body = @{
  device_id = "esp32s3-inmp441-worker-01"
  name = "ESP32-S3 INMP441 Worker 01"
  public_key = "9"
  location = "Ruang 1"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8000/api/devices" `
  -ContentType "application/json" `
  -Body $body
```

Respons `409 Conflict` berarti ID tersebut sudah terdaftar dan tidak perlu dibuat lagi.

## Upload Firmware

1. Buka file `.ino` di Arduino IDE.
2. Salin `config.example.h` menjadi `config.h`, lalu isi `WIFI_SSID`, `WIFI_PASSWORD`, dan `SERVER_BASE_URL` lokal.
3. Pilih board ESP32-S3 yang sesuai.
4. Pastikan pin INMP441, LED, dan buzzer sesuai tabel.
5. Compile lalu upload firmware.
6. Buka Serial Monitor pada baud rate yang ditentukan firmware.
7. Mulai berbicara saat LED indikator perekaman menyala.

## Menjalankan Fine-Tuning IndoBERT

Notebook dapat dibuka langsung:

```text
dataset/train_bert_final_dataset.ipynb
```

Atau jalankan runner:

```powershell
python dataset\run_full_finetune_indobert.py
```

Untuk memantau log secara terus-menerus:

```powershell
Get-Content dataset\full_finetune_indobert_runner.log -Wait
```

Model hasil training ditempatkan di `backend/bert/trained_model_indobert_full` dan dipilih melalui `BERT_MODEL_NAME` pada `.env`.

## Menjalankan Pengujian

```powershell
$env:TMP="$PWD\.tmp_pytest"
$env:TEMP="$PWD\.tmp_pytest"
python -m pytest -q
```

Pengujian meliputi API, ZKP, token, preprocessing audio, auto-correct bahasa Indonesia, aturan keyword darurat, dan pipeline klasifikasi.

## Keadaan Dashboard

- **Hijau:** event terbaru diklasifikasikan sebagai `Normal`.
- **Merah:** event terbaru diklasifikasikan sebagai `Emergency`.
- **Abu-abu:** browser tidak dapat menghubungi backend.
- Lokasi perangkat sementara ditampilkan sebagai **Ruang 1**.
- Jam menggunakan zona **Asia/Jakarta (WIB)**.

## Batasan Prototype

- Audio dan klasifikasi hanya difokuskan pada bahasa Indonesia.
- Klasifikasi hanya memiliki kelas `Normal` dan `Emergency`.
- ZKP menggunakan bilangan kecil untuk demonstrasi, bukan keamanan produksi.
- Sistem membutuhkan Wi-Fi dan backend aktif.
- Sistem hanya memberi peringatan dan tidak menggantikan tindakan petugas.
- Kualitas transkripsi tetap dipengaruhi jarak bicara, kebisingan, pemasangan mikrofon, dan kualitas jaringan.

## Troubleshooting Singkat

### Port 8000 sudah digunakan

```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
```

Hentikan hanya proses backend lama yang memang tidak dipakai, atau jalankan server di port lain.

### ESP32 tidak dapat upload

- Pastikan IP server pada firmware benar.
- Izinkan Python/port 8000 pada Windows Firewall.
- Pastikan laptop dan ESP32 menggunakan Wi-Fi yang sama.
- Pastikan backend menampilkan `Application startup complete`.

### Buzzer tidak menyala

- Pastikan hasil akhir backend benar-benar `Emergency`.
- Periksa polaritas buzzer dan kesamaan ground.
- Uji GPIO 9 menggunakan LED sebelum memasang buzzer kembali.

### Transkripsi kurang tepat

- Bicara 15-30 cm dari INMP441.
- Arahkan lubang mikrofon ke pembicara.
- Hindari menutup sensor atau meletakkannya dekat buzzer.
- Periksa statistik audio pada Serial Monitor dan log backend.

## Catatan Komentar Kode

Komentar mengikuti sintaks bahasa masing-masing: Python memakai `#` dan docstring, Arduino/JavaScript memakai `//`, HTML memakai `<!-- -->`, serta CSS memakai `/* */`. Komentar ditempatkan per blok logika agar kode tetap valid dan lebih mudah dijelaskan; komentar pada setiap baris sederhana sengaja dihindari karena dapat menutupi alur program.
=======
# VoiceGuard-ZKP-Sistem-IoT-Cerdas-untuk-Deteksi-Kondisi-Darurat-Berbasis-Suara-dengan-Autentikasi-ZKP
VoiceGuard ZKP adalah sistem deteksi kondisi darurat pekerja berbasis suara. Audio diproses menggunakan Whisper untuk menghasilkan teks, lalu diklasifikasikan oleh IndoBERT menjadi Emergency atau Normal. Sistem menggunakan Schnorr Zero-Knowledge Proof untuk autentikasi perangkat dan mengirim notifikasi saat kondisi darurat terdeteksi.
>>>>>>> 0bddb76 (Initial commit)
