# Panduan Produksi Video VoiceGuard-ZKP

## Spesifikasi

- Durasi target: 68 detik
- Rasio: 16:9 horizontal
- Resolusi: 1920x1080
- Frame rate: 24 atau 30 fps
- Gaya: animasi stickman 2D, motion graphic minimalis
- Pekerja: stickman biru tua, helm kuning
- Petugas: stickman hijau, helm putih
- Normal: hijau; teknologi: biru; bahaya: merah
- Hindari darah, luka terbuka, gerakan tubuh tidak wajar, perubahan desain karakter, teks acak, dan kamera berguncang.

Gunakan `00-character-sheet.png` sebagai referensi karakter pada semua klip. Untuk generator image-to-video, unggah gambar adegan terkait sebagai frame awal dan pertahankan komposisinya.

## Storyboard dan Urutan Editing

| Adegan | Waktu | Keyframe | Isi dan gerakan | Narasi | Teks layar | Audio |
|---|---:|---|---|---|---|---|
| 1. Kondisi normal | 00:00–00:06 | `01-kondisi-normal.png` | Pekerja berjalan ke kanan; kamera pan perlahan; LED alat berkedip lembut. | "Di area kerja, VoiceGuard-ZKP memantau suara secara terus-menerus." | Sistem pemantauan keselamatan berbasis suara | Musik korporat tenang, langkah kaki, ambience gudang |
| 2. Kecelakaan | 00:06–00:11 | `02-kecelakaan.png` | Kardus jatuh dan berhenti di kaki; pekerja terduduk; sedikit camera punch-in. | "Sebuah kardus tiba-tiba jatuh dan menimpa kaki pekerja." | — | Bunyi kardus jatuh “DUK!”, musik mulai tegang |
| 3. Meminta tolong | 00:11–00:17 | `03-meminta-pertolongan.png` | Tangan pekerja terangkat; gelembung ucapan muncul; gelombang suara bergerak ke alat. | "Pekerja segera berteriak meminta pertolongan." | Tolong! Kaki saya tertimpa kardus! | Dialog korban, gema ringan, whoosh gelombang suara |
| 4. Suara ditangkap | 00:17–00:23 | `04-perangkat-menangkap-suara.png` | Zoom ke alat; mikrofon dan LED berdenyut; ikon bukti bergerak menuju server. | "Perangkat menangkap suara dan membuktikan identitasnya tanpa mengirimkan secret key." | Suara terdeteksi • ESP8266 Worker 01 • Area Produksi A | Beep deteksi, digital confirmation |
| 5. Audio dikirim | 00:23–00:28 | `05-audio-ke-server.png` | Paket audio meluncur ke server; gembok mengunci; centang muncul. | "Setelah terverifikasi, audio dikirim ke backend untuk diproses." | Audio dikirim ke backend | Data whoosh, lock click |
| 6. Machine learning | 00:28–00:36 | `06-pipeline-machine-learning.png` | Sorot setiap tahap secara berurutan; transcript diketik; hasil merah muncul terakhir. | "Whisper mengubah suara menjadi teks. IndoBERT kemudian mengklasifikasikannya sebagai keadaan darurat dengan confidence sembilan puluh empat persen." | Audio → Whisper → IndoBERT → Emergency 94% | Bunyi proses berurutan, keyboard ringan, alert hit |
| 7. Dashboard berubah | 00:36–00:43 | `07-dashboard-berubah.png` | Sapuan diagonal mengubah hijau menjadi merah; lokasi dan identitas alat diperbesar. | "Dashboard langsung berubah dari kondisi normal menjadi bahaya dan menunjukkan lokasi sumber suara." | BAHAYA TERDETEKSI • Area Produksi A | Rising alert, satu bunyi sirene pendek |
| 8. Notifikasi petugas | 00:43–00:49 | `08-notifikasi-petugas.png` | Notifikasi bergerak dari server ke ponsel; ponsel bergetar; petugas menoleh. | "Peringatan otomatis dikirim kepada petugas keselamatan." | PERINGATAN DARURAT • Area Produksi A • Emergency 94% | Notification ping, getaran ponsel |
| 9. Respons cepat | 00:49–00:56 | `09-petugas-merespons.png` | Petugas datang dari kiri; satu mengangkat kardus, satu membantu korban; first-aid kit muncul. | "Berdasarkan lokasi perangkat, petugas segera tiba dan memberikan pertolongan." | Area Produksi A | Langkah cepat, geser kardus, musik berubah optimistis |
| 10. Kondisi ditangani | 00:56–01:02 | `10-kondisi-ditangani.png` | Petugas memberi jempol; korban aman; panel hijau dan centang masuk dengan fade. | "Kondisi berhasil ditangani dan sistem kembali dalam status aman." | Kondisi telah ditangani • Petugas tiba di lokasi | Success chime, ambience tenang |
| 11. Penutup | 01:02–01:08 | `11-penutup.png` | Kamera perlahan mendekat; empat ikon muncul satu per satu; judul fade-in. | "VoiceGuard-ZKP: mendengar, memahami, mendeteksi, dan membantu mempercepat respons darurat." | Deteksi suara dan respons darurat yang lebih cepat | Musik resolusi, logo sting lembut |

## Prompt Image-to-Video per Klip

Tambahkan instruksi global berikut pada setiap prompt:

> Preserve the exact 2D stickman character design, colors, helmets, warehouse layout, VoiceGuard-ZKP device, and flat vector style from the input frame. Smooth professional motion graphic animation, stable geometry, horizontal 16:9, no camera shake, no new characters, no morphing, no realistic humans, no 3D, no blood, no wounds, no random text, no watermark.

### Klip 1 — Kondisi Normal

> Animate the navy stickman worker walking smoothly from left to right through the warehouse. Use a slow camera pan following him. Add subtle warehouse ambience, slight parallax on shelves and boxes, and a gentle green pulse on the VoiceGuard-ZKP LED. Keep all boxes stable and the mood calm. Duration 6 seconds.

### Klip 2 — Kecelakaan

> Animate one cardboard box tipping from the stack, falling with believable simple 2D motion, and stopping against the worker's foot. The navy worker loses balance and sits down safely. Add brief impact lines and a small alert symbol, without showing injury. Use a subtle quick camera push-in at impact. Duration 5 seconds.

### Klip 3 — Meminta Pertolongan

> Animate the seated navy worker raising one hand and calling for help. Make the speech bubble appear with a soft pop. Send three to five blue sound-wave arcs from the worker toward the wall-mounted VoiceGuard-ZKP device. Make the device microphone and green LED begin pulsing when the waves arrive. Duration 6 seconds.

### Klip 4 — Perangkat dan Autentikasi

> Slowly zoom toward the VoiceGuard-ZKP device. Pulse the microphone glow in sync with the incoming sound waves. Reveal the status information line by line. Animate the security flow from device to proof to server to verified shield, ending with a green check. Duration 6 seconds.

### Klip 5 — Audio ke Backend

> Animate the blue audio-file packet moving quickly from the VoiceGuard-ZKP device to the server along the dotted path. Add motion streaks. Close the green padlock as the packet passes, then illuminate the server lights and show a green verification check. Duration 5 seconds.

### Klip 6 — Pipeline Machine Learning

> Animate the processing pipeline stage by stage from left to right. Pulse the audio waveform, illuminate Whisper, type the transcript progressively, illuminate IndoBERT, then reveal Normal 6% followed by a stronger red Emergency 94% result. Keep the final emergency alert clear and restrained. Duration 8 seconds.

### Klip 7 — Dashboard Berubah

> Animate a clean diagonal sweep transforming the dashboard from green normal state into red danger state. Morph only the status colors and alert content while preserving the interface layout. Pulse the red alert shield once. Zoom attention toward ESP8266 Worker 01 and Area Produksi A, then reveal the transcript and confidence. Duration 7 seconds.

### Klip 8 — Notifikasi Petugas

> Animate a red emergency signal traveling from the server to the smartphone. Make the phone vibrate gently and display the emergency card. The two green safety officers turn toward the phone; one points to Area Produksi A. End with a green sent check. Duration 6 seconds.

### Klip 9 — Respons Cepat

> Animate the two green safety officers arriving quickly from the left. One safely lifts and moves the cardboard box away from the worker's foot while the second kneels and supports the worker's shoulder. Bring the first-aid kit into view. Use calm controlled movements, not frantic action. Duration 7 seconds.

### Klip 10 — Kondisi Ditangani

> Animate the resolved warehouse scene gently. The worker sits safely and breathes calmly. One officer gives a thumbs-up; the other holds the first-aid kit. Pulse the VoiceGuard-ZKP LED green. Fade in the green resolved status panel and shield check. Duration 6 seconds.

### Klip 11 — Penutup

> Use a slow centered camera push toward the VoiceGuard-ZKP device. Reveal the microphone, shield, machine-learning, and notification icons one by one around it. Draw the circular connector line, then reveal the four-step process from left to right. Fade in the title and subtitle last. Duration 6 seconds.

## Naskah Narasi Utuh

> Di area kerja, VoiceGuard-ZKP memantau suara secara terus-menerus. Sebuah kardus tiba-tiba jatuh dan menimpa kaki pekerja. Pekerja segera berteriak meminta pertolongan. Perangkat menangkap suara dan membuktikan identitasnya tanpa mengirimkan secret key. Setelah terverifikasi, audio dikirim ke backend untuk diproses. Whisper mengubah suara menjadi teks. IndoBERT kemudian mengklasifikasikannya sebagai keadaan darurat dengan confidence sembilan puluh empat persen. Dashboard langsung berubah dari kondisi normal menjadi bahaya dan menunjukkan lokasi sumber suara. Peringatan otomatis dikirim kepada petugas keselamatan. Berdasarkan lokasi perangkat, petugas segera tiba dan memberikan pertolongan. Kondisi berhasil ditangani dan sistem kembali dalam status aman. VoiceGuard-ZKP: mendengar, memahami, mendeteksi, dan membantu mempercepat respons darurat.

## Dialog Korban

> Tolong! Kaki saya tertimpa kardus! Saya membutuhkan bantuan!

## Pengaturan Audio

- Narator: suara tenang, jelas, profesional, kecepatan sekitar 140–150 kata/menit.
- Dialog korban: lebih keras dari narator, terdengar mendesak tetapi tidak berlebihan.
- Musik: satu trek korporat/teknologi; tenang pada awal, tegang pada kecelakaan, optimistis setelah petugas tiba.
- Turunkan musik sekitar 8–12 dB saat narasi atau dialog berlangsung.
- Batasi sirene menjadi satu bunyi pendek agar narasi tetap jelas.

## Urutan Editing di CapCut/Canva

1. Buat proyek 1920x1080, 24 atau 30 fps.
2. Masukkan klip sesuai nomor 01–11.
3. Potong durasi sesuai tabel storyboard hingga total 68 detik.
4. Gunakan transisi sederhana: cut, dissolve 6–10 frame, dan diagonal wipe khusus adegan 7.
5. Tambahkan narasi terlebih dahulu, lalu sesuaikan titik perpindahan visual dengan kalimat narasi.
6. Masukkan dialog korban pada detik 12–16.
7. Tambahkan efek suara sesuai tabel, kemudian musik latar.
8. Impor `voiceguard-zkp-subtitles.srt` untuk subtitle.
9. Gunakan font sans-serif putih dengan outline navy; maksimal dua baris subtitle.
10. Ekspor H.264 MP4, 1080p, bitrate 10–16 Mbps, audio AAC 48 kHz.

## Negative Prompt Umum

> realistic human, detailed anatomy, 3D render, photorealistic, inconsistent stickman proportions, changing helmet color, changing character color, extra limbs, extra characters, morphing device, changing warehouse layout, blood, wounds, gore, frightening injury, random text, misspelled text, unreadable UI, shaky camera, rapid flicker, neon cyberpunk, dark horror lighting, watermark, logo distortion
