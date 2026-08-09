# Frontend dan Perangkat IoT

Folder ini berisi bagian yang berinteraksi langsung dengan pengguna dan perangkat lapangan.

## Struktur

```text
frontend/
|-- firmware/
|   |-- esp32_inmp441/     Firmware aktif ESP32-S3 + INMP441
|   `-- esp8266/           Firmware analog lama sebagai referensi
`-- docs/
    |-- images/            Screenshot, flowchart, dan prototype
    |-- guides/            Panduan tambahan
    `-- video_storyboard/  Materi visual presentasi
```

Dashboard web saat ini disajikan langsung oleh FastAPI dari `backend/api/v1/monitoring.py`. Pendekatan ini sengaja dipertahankan agar prototype hanya membutuhkan satu server dan tidak menambah proses build frontend terpisah.

## Dashboard

Dashboard mengambil data berikut setiap satu detik:

- `GET /api/monitoring/overview` untuk statistik 24 jam.
- `GET /api/monitoring/events` untuk event, transkrip, label, dan confidence terbaru.

Event terbaru mengendalikan warna utama:

- `Normal` menghasilkan tampilan hijau.
- `Emergency` menghasilkan tampilan merah dan animasi peringatan.
- Kegagalan koneksi menghasilkan tampilan offline.

## Firmware Aktif

Gunakan:

```text
frontend/firmware/esp32_inmp441/esp32_inmp441_emergency_detector/esp32_inmp441_emergency_detector.ino
```

Firmware ESP8266 tetap disimpan sebagai referensi sejarah pengembangan, tetapi bukan konfigurasi perangkat utama saat ini.

Sebelum compile firmware aktif, salin `config.example.h` menjadi `config.h` di folder sketch lalu isi SSID, password Wi-Fi, dan alamat backend. File `config.h` tidak dilacak Git agar kredensial lokal tidak terunggah.
