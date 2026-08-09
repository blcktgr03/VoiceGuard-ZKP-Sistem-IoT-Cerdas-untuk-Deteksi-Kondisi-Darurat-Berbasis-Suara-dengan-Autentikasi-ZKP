# Presentation Guide — VoiceGuard-ZKP

**Presenter:** Muhamad Umar Nugroho — **2322101943** — **III RPKK**  
**Target duration:** 15–18 menit + 2–3 menit Q&A  
**Recommended slides:** 16

## Slide Sequence

| Slide | Title | Main point | Visual wajib |
|---:|---|---|---|
| 1 | VoiceGuard-ZKP | Judul, identitas, one-line value | Foto prototype + logo |
| 2 | Current Challenge | Darurat sulit dilaporkan saat device tidak terjangkau | Ilustrasi pekerja tertimpa |
| 3 | Why Voice? | Hands-free emergency channel; bukan satu-satunya sensor | Voice wave + tombol fallback |
| 4 | Goal & Scope | Normal/Emergency Indonesia, device terdaftar, lokasi/alert | Scope in/out diagram |
| 5 | R&D Method | Need→design→build→test→evaluate | Cycle diagram |
| 6 | System Overview | Device→auth→STT→ML→dashboard | End-to-end architecture |
| 7 | Device & Audio | 16kHz, mono, 3s, INMP441, LED/buzzer | Pin/device diagram |
| 8 | Dataset | 54.656; 51,34/48,66 | Class donut/bar |
| 9 | Data Quality | Missing 0; 13 conflicts; split 80/10/10 | Data quality cards |
| 10 | Machine Learning | Whisper→autocorrect→IndoBERT→rules | ML pipeline |
| 11 | Why IndoBERT? | Contextual Indonesian model vs baselines | Model comparison bar |
| 12 | Results | Accuracy 90,61; F1 90,14 | Metric cards |
| 13 | Error Analysis | FP 197; FN 316; FN priority | Confusion matrix |
| 14 | ZKP & Security | Prove secret knowledge, not encrypt audio | 3-arrow Schnorr flow |
| 15 | Demo & Verification | dashboard/device/location; 34 tests | Normal vs danger UI |
| 16 | Limits & Development | noise, streaming, secure channel, field test | Four-step roadmap |

## Opening Script

“Bayangkan seorang pekerja tertimpa benda dan tidak dapat mengambil telepon. Ia masih mungkin berteriak meminta bantuan. VoiceGuard-ZKP mencoba menjadikan suara itu sebagai kanal peringatan tambahan: perangkat menangkap audio, server memahami teks, menunjukkan lokasi, dan memberi alert. Proyek ini tidak menggantikan petugas atau tombol darurat; fokusnya adalah mempercepat informasi awal.”

## Key Technical Explanation

### Whisper vs IndoBERT

“Whisper menjawab *apa yang diucapkan*. IndoBERT menjawab *apakah isi teks itu Normal atau Emergency*. Autocorrect hanya mapping typo ASR yang telah ditinjau, bukan model ML terpisah.”

### Stratify and Random State

“Stratify menjaga persentase Normal dan Emergency tetap mirip pada train, validation, dan test. Random state 42 membuat pembagian sama saat kode dijalankan ulang.”

### Metrics

“Accuracy model 90,61%, tetapi saya tidak berhenti di accuracy. Recall Emergency 88,12% berarti masih ada 316 Emergency yang terlewat. Karena itu sistem belum boleh menjadi satu-satunya alarm.”

### ZKP

“Perangkat membuktikan bahwa ia mengetahui secret key tanpa mengirim secret tersebut. Server memeriksa persamaan Schnorr. Ini mengautentikasi perangkat, tetapi audio tetap membutuhkan TLS, integritas pesan, dan anti-replay.”

## Demo Flow

1. Buka `/api/health` dan dashboard hijau.
2. Tunjukkan device ID dan lokasi.
3. Jalankan challenge dan verification.
4. Ucapkan kalimat normal; tunjukkan transkrip/status hijau.
5. Ucapkan “tolong, kaki saya tertimpa”; tunjukkan merah, lokasi, confidence, buzzer/notifikasi.
6. Tunjukkan satu negasi: “semua aman, tidak butuh bantuan”.
7. Tutup dengan keterbatasan dan fallback.

Backup: screenshot UI normal/danger, hasil Swagger, confusion matrix, dan video pendek. Jangan mengandalkan demo jaringan tunggal.

## Questions and Answers

**Mengapa suara bila industri bising?**  
Suara dipilih sebagai kanal hands-free tambahan, bukan pengganti sensor/tombol. Noise adalah risiko utama dan belum selesai diuji; roadmap mencakup SNR, masker, jarak, dan multimodal fallback.

**Mengapa IndoBERT bukan Random Forest?**  
IndoBERT memproses urutan dan konteks bahasa Indonesia. Random Forest memerlukan vectorization dan kurang efisien pada ruang TF-IDF sangat besar. Baseline yang lebih natural untuk teks—Logistic Regression, LinearSVC, dan Naive Bayes—sudah dibandingkan.

**Apakah ZKP mengenkripsi suara?**  
Tidak. ZKP membuktikan pengetahuan secret perangkat. Kerahasiaan audio memerlukan TLS/encryption; integritas dan freshness memerlukan message binding, timestamp/counter, serta anti-replay.

**Mengapa satu epoch?**  
Itu konfigurasi awal yang membatasi biaya komputasi dan memberi hasil cukup baik, tetapi belum tuning optimal. Klaim hanya berdasarkan konfigurasi yang benar-benar dijalankan.

**Apa bukti sistem bekerja?**  
Artefak model, API/dashboard/firmware tersedia; 34 tests lulus; test classifier terukur. Yang belum ada adalah benchmark lapangan audio end-to-end dan security/reliability production.

**Apa prioritas pengembangan?**  
Pertama keselamatan/security: recall, local fallback, TLS, message binding, credential cleanup. Kedua bukti lapangan. Ketiga streaming dan deployment scale.

## Closing Script

“VoiceGuard-ZKP menunjukkan feasibility integrasi suara, machine learning, identitas perangkat, lokasi, dan alert. Model mencapai F1 Emergency 90,14% dan seluruh 34 test lulus. Namun nilai utama kesimpulan saya adalah batasnya jelas: sistem masih prototipe dan harus ditingkatkan pada recall, noise, jaringan, serta keamanan sebelum digunakan di lapangan.”

