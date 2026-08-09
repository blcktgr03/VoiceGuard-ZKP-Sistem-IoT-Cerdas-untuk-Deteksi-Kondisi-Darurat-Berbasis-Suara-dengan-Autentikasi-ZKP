# Project Proposal: VoiceGuard-ZKP

**Nama:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Domain:** NLP/Speech Processing, IoT, dan keamanan perangkat  
**Versi proposal:** 1.0

## Executive Summary

VoiceGuard-ZKP dirancang sebagai prototipe pendukung keselamatan pekerja yang dapat menerima indikasi darurat melalui suara ketika korban sulit menjangkau telepon atau tombol alarm. ESP32-S3 dan mikrofon INMP441 merekam audio tiga detik, perangkat membuktikan identitasnya melalui Schnorr ZKP, lalu backend mentranskripsikan audio dengan faster-whisper dan mengklasifikasikan teks dengan IndoBERT serta aturan darurat. Hasil berupa identitas perangkat, lokasi, transkrip, label, confidence, notifikasi, dan status buzzer ditampilkan agar petugas dapat merespons lebih cepat.

Nilai utama proyek bukan menggantikan prosedur K3, melainkan menyediakan **kanal deteksi tambahan berbasis suara**. Keberhasilan prototipe dinilai dari performa klasifikasi, kemampuan autentikasi perangkat, keberhasilan pipeline upload-ke-dashboard, dan keterbukaan terhadap keterbatasan kondisi bising, jaringan, keamanan stream, serta false negative.

## 1. Problem Statement

### 1.1 Business Context

Kondisi darurat di tempat kerja dapat membuat korban tidak mampu mengambil telepon, menekan tombol, atau berpindah ke titik alarm. Dalam situasi seperti tertimpa barang, terjepit, jatuh, kebakaran, atau melihat rekan cedera, respons yang masih mungkin dilakukan adalah berteriak atau meminta bantuan secara verbal. Jeritan memiliki karakteristik akustik yang kuat dalam menarik perhatian, tetapi suara tetap hanya dijadikan kanal tambahan karena kebisingan, masker, respirator, jarak mikrofon, dan gangguan jaringan dapat menurunkan kualitasnya.

Stakeholder utama ialah pekerja, petugas K3, supervisor, security, tim tanggap darurat, pengelola fasilitas, dan administrator sistem. Tanpa sistem yang menghubungkan suara, identitas perangkat, lokasi, dan notifikasi, petugas dapat menerima informasi terlambat atau tanpa konteks lokasi. Di sisi lain, perangkat palsu tidak boleh bebas mengirim alarm; karena itu autentikasi perangkat menjadi kebutuhan terpisah dari klasifikasi suara.

Masalah ini relevan karena paparan proyek mengacu pada besarnya dampak kecelakaan kerja secara global serta kajian IoT keselamatan. Namun, statistik makro hanya menjadi motivasi, bukan bukti bahwa VoiceGuard-ZKP sendiri telah menurunkan kecelakaan. Dampak riil harus dibuktikan melalui uji lapangan terkontrol.

### 1.2 Problem Definition

**Masalah inti:** bagaimana membangun prototipe yang dapat menerima audio bahasa Indonesia dari perangkat terdaftar, mengubahnya menjadi teks, membedakan kondisi Normal dan Emergency, menampilkan lokasi kejadian, dan mengirim alert secara cukup cepat serta dapat diaudit.

Rumusan masalah:

1. Bagaimana merancang alat keselamatan berbasis suara untuk menangkap indikasi keadaan darurat?
2. Bagaimana mengubah audio bahasa Indonesia menjadi teks yang layak diklasifikasikan?
3. Bagaimana mengklasifikasikan teks sebagai Normal atau Emergency dengan performa terukur?
4. Bagaimana memvalidasi perangkat tanpa mengirim secret key ke server?
5. Bagaimana mengintegrasikan perangkat, ML, dashboard, dan notifikasi dalam satu alur?
6. Apa batas keamanan, latency, reliability, dan generalisasi prototipe saat ini?

### 1.3 SMART Problem Statement

Dalam dua minggu kegiatan capstone, membangun dan mendokumentasikan prototipe VoiceGuard-ZKP yang memproses chunk WAV 3 detik dari ESP32-S3 terdaftar, menghasilkan transkrip dan klasifikasi biner bahasa Indonesia, mencapai F1 Emergency minimal 0,90 pada held-out test set, menyediakan API/dashboard/notifikasi, serta melaporkan false positive, false negative, keterbatasan keamanan, dan gap pengujian produksi.

| Unsur SMART | Pemenuhan |
|---|---|
| Specific | Audio Indonesia → STT → koreksi terbatas → klasifikasi Normal/Emergency → dashboard/alert |
| Measurable | F1, precision, recall, confusion matrix, test API, dan latency komponen |
| Achievable | Memakai model pralatih dan perangkat yang tersedia; ruang lingkup hanya dua kelas |
| Relevant | Menambah kanal peringatan ketika akses fisik ke perangkat komunikasi terbatas |
| Time-bound | Milestone Week 13–14 sesuai Lab 12; status akhir didokumentasikan per 4 Agustus 2026 |

## 2. Project Scope

### 2.1 Project Objective

**Tujuan utama:** menghasilkan prototipe sistem peringatan darurat berbasis suara yang menghubungkan perangkat terdaftar dengan pipeline ML dan dashboard lokasi.

Tujuan khusus:

1. Merekam audio digital mono 16 kHz melalui INMP441 dan ESP32-S3.
2. Mengautentikasi perangkat melalui challenge-response Schnorr tanpa mengirim secret key.
3. Mentranskripsikan bahasa Indonesia menggunakan faster-whisper Small.
4. Mengoreksi alias ASR yang telah ditinjau tanpa mengganti kata valid secara agresif.
5. Mengklasifikasikan teks dengan IndoBERT dan kebijakan aturan darurat.
6. Menyimpan event, menampilkan perangkat/lokasi/transkrip, dan mengirim notifikasi.
7. Mengukur performa klasifikasi dan mengidentifikasi false alarm serta missed emergency.

### 2.2 In Scope

- Bahasa Indonesia.
- Klasifikasi biner `Normal` dan `Emergency`.
- Satu atau beberapa perangkat terdaftar dengan identitas dan lokasi statis.
- Audio WAV 16-bit mono, 16 kHz, chunk 3 detik.
- ESP32-S3, INMP441, LED, dan buzzer.
- FastAPI, SQLite, dashboard web, dan Telegram opsional.
- Autentikasi perangkat Schnorr dengan parameter demo.
- Full fine-tuning IndoBERT dan eksperimen baseline TF-IDF.
- Pengujian unit pada API, token, ZKP, audio preprocessing, autocorrect, dan pipeline.

### 2.3 Out of Scope

- Diagnosis medis, penentuan tingkat cedera, atau pengambilan keputusan evakuasi otomatis.
- Penggantian tombol emergency, radio, CCTV, SOP K3, atau petugas manusia.
- Bahasa selain Indonesia dan klasifikasi multikelas jenis insiden.
- Sertifikasi perangkat keselamatan, high availability, dan skala pabrik penuh.
- Pengenalan identitas pembicara atau biometrik suara.
- Jaminan keamanan produksi; parameter Schnorr saat ini hanya demonstrasi.
- Streaming audio kontinu sejati; implementasi aktif masih berupa chunk rekam-kirim-proses.

### 2.4 Data Description

#### Data Source

Paparan mendokumentasikan empat kelompok sumber:

| Sumber | Isi/Kegunaan yang didokumentasikan |
|---|---|
| MEDISCO | Ujaran bahasa Indonesia domain medis seperti sakit, terluka, dan bantuan |
| IndSpeech/TelDialog | Percakapan bahasa Indonesia dan konteks layanan darurat |
| SVCSR/ASR-IndoCSC | Percakapan sehari-hari untuk membedakan ucapan biasa |
| HumAID | Teks bencana seperti kebakaran, banjir, gempa, dan evakuasi |

Dataset final tidak memiliki kolom `source`, `speaker`, `noise_level`, atau `mask_condition`. Karena itu, kontribusi setiap sumber dan potensi overlap speaker tidak dapat diaudit langsung dari CSV final; ini dicatat sebagai keterbatasan provenance.

#### Dataset Characteristics

| Atribut | Nilai terverifikasi |
|---|---:|
| Ukuran | 54.656 baris × 3 kolom |
| Fitur input utama | `text` |
| Target | `label`: 0 Normal, 1 Emergency |
| Kolom label terbaca | `label_name` |
| Normal | 28.058 (51,3356%) |
| Emergency | 26.598 (48,6644%) |
| Missing values | 0 |
| Empty text | 0 |
| Full-row duplicates | 0 |
| Unique text | 54.643 |
| Conflicting duplicate texts | 13 teks |
| Rata-rata panjang | 88,02 karakter / 13,21 kata |
| Maksimum panjang | 494 karakter / 73 kata |

Pembagian data menggunakan dua tahap `train_test_split`, `stratify`, dan `random_state=42`: train 43.724 (80%), validation 5.466 (10%), test 5.466 (10%).

### 2.5 Success Metrics

| Metrik | Target | Alasan | Hasil/status |
|---|---:|---|---|
| F1 Emergency | ≥0,90 | Menyeimbangkan precision dan recall | **0,9014 — tercapai** |
| Precision Emergency | ≥0,90 | Mengurangi alarm palsu | **0,9225 — tercapai** |
| Recall Emergency | ≥0,90 | Mengurangi kondisi bahaya yang terlewat | **0,8812 — belum tercapai** |
| Accuracy test | ≥0,90 | Ringkasan performa umum pada kelas hampir seimbang | **0,9061 — tercapai** |
| False alarm rate pada Normal | ≤8% | Membatasi gangguan operasional | **7,02% — tercapai pada test teks** |
| Miss rate pada Emergency | ≤10% | Batas keselamatan awal | **11,88% — belum tercapai** |
| Unit/API tests | 100% lulus | Menilai stabilitas logika yang diuji | **34/34 lulus** |
| Latency audio-ke-alert | ≤5 detik | Alert harus cepat | **Belum diukur end-to-end** |
| Uji industrial noise/mask | Recall ≥0,85 | Kelayakan lingkungan sasaran | **Belum diuji** |
| Replay/fake device rejection | 100% pada skenario uji | Mencegah sumber alert palsu | **Belum diuji menyeluruh** |

Primary metric adalah **Recall Emergency** untuk konteks keselamatan, meskipun F1 dipakai sebagai target model karena false positive juga memengaruhi kepercayaan operator.

### 2.6 Constraints & Requirements

#### Technical Constraints

- CPU menjadi target backend saat ini; model BERT dan Whisper masing-masing hampir 500 MB.
- Audio diproses berurutan per chunk dan membutuhkan Wi-Fi serta server aktif.
- Input firmware adalah 3 detik, sehingga latency total minimal sudah mencakup durasi capture tersebut.
- Model dilatih dengan `max_length=64`, tetapi service inferensi saat ini memakai `max_length=512`; konfigurasi ini perlu disamakan.
- Tidak ada Dockerfile dan belum ada pengujian concurrency/load.

#### Data Constraints

- Label hanya dua kelas dan dapat menyederhanakan ragam kondisi nyata.
- Dataset final kehilangan metadata sumber, speaker, jenis noise, masker, dan perangkat.
- Terdapat 13 konflik label serta 3 overlap teks antarsplit yang terdeteksi.
- Distribusi kelas seimbang, sehingga SMOTE tidak diperlukan pada dataset final; penggunaan SMOTE yang disebut paparan perlu dibuktikan dan hanya boleh diterapkan pada train set.

#### Security and Privacy Constraints

- Audio dapat mengandung data pribadi dan percakapan sensitif; diperlukan consent, retensi minimum, kontrol akses, dan penghapusan terjadwal.
- ZKP hanya membuktikan identitas/pengetahuan secret, bukan kerahasiaan audio.
- HTTP biasa harus diganti HTTPS/TLS.
- Proof perangkat interaktif belum mengikat hash audio; replay dan message substitution masih perlu mitigasi.
- Parameter `p=23`, `q=11`, `g=2` bukan parameter produksi.
- Source firmware masih memuat konfigurasi Wi-Fi secara hardcoded; rahasia harus dipindah sebelum publikasi/deployment.

#### Business Constraints

- Sistem hanya alat bantu; keputusan dan respons tetap dilakukan petugas.
- Alarm palsu yang sering akan menyebabkan alarm fatigue.
- False negative lebih berbahaya dan harus menjadi prioritas pengembangan.
- Implementasi lapangan memerlukan izin K3, kebijakan privasi, dan fallback manual.

## 3. Proposed Approach

### 3.1 Research and Development Method

Metode R&D dipilih karena keluaran proyek bukan hanya analisis model, tetapi **produk prototipe terpadu**. Tahapannya ialah: identifikasi kebutuhan → desain arsitektur → pengumpulan/persiapan data → pengembangan firmware/backend/model → integrasi → pengujian → evaluasi → revisi. Metode ini masuk akal karena kualitas produk harus dinilai sekaligus dari model, perangkat, jaringan, keamanan, UI, dan notifikasi.

### 3.2 High-Level Strategy

```text
Ucapan pekerja
  → INMP441 menangkap PCM digital
  → ESP32-S3 membentuk WAV 16 kHz/16-bit/mono selama 3 detik
  → Schnorr challenge-response mengautentikasi device
  → HMAC token sementara mengizinkan upload
  → FastAPI menyimpan audio dan metadata
  → filter aktivitas suara + normalisasi WAV
  → faster-whisper Small menghasilkan teks Indonesia
  → autocorrect alias ASR yang telah direview
  → IndoBERT + aturan kata/negasi menghasilkan Normal/Emergency
  → SQLite + dashboard + Telegram + server proof
  → respons kembali ke device, buzzer aktif bila Emergency
```

### 3.3 Algorithm Selection

| Kandidat | Peran | Kelebihan | Kekurangan |
|---|---|---|---|
| Dummy most-frequent | Baseline bawah | Sangat sederhana | Tidak mengenali Emergency |
| TF-IDF + Logistic Regression | Baseline linear | Cepat, relatif mudah dijelaskan | Konteks dan negasi terbatas |
| TF-IDF + LinearSVC | Baseline kuat | Cepat dan efektif untuk teks | Confidence tidak langsung terkalibrasi |
| TF-IDF + MultinomialNB | Pembanding probabilistik | Sangat cepat | Asumsi independensi kata sederhana |
| IndoBERT | Model final | Representasi kontekstual bahasa Indonesia | Berat, sulit dijelaskan, memerlukan fine-tuning |
| Aturan keyword/negasi | Safety guardrail | Menutup beberapa error yang jelas | Dapat menciptakan false positive dan perlu audit |

IndoBERT dipilih karena bahasa Indonesia, konteks, dan negasi lebih relevan dibanding model bag-of-words. Sistem final tetap hibrida karena smoke test menemukan beberapa kalimat darurat dapat diprediksi Normal oleh model murni.

### 3.4 Configuration

| Parameter | Nilai | Alasan |
|---|---:|---|
| Base model | `indobenchmark/indobert-base-p1` | Telah pretraining pada teks Indonesia |
| Max length training | 64 token | Ujaran relatif pendek; 99% data ≤36 kata secara pendekatan jumlah kata |
| Batch size | 8 | Menyesuaikan memori perangkat training |
| Epoch | 1 | Membatasi waktu/overfitting; dipilih sebagai eksperimen awal, belum tuning penuh |
| Learning rate | 2e-5 | Nilai konservatif umum untuk fine-tuning BERT |
| Random seed | 42 | Reproducible split/training |
| Split | 80/10/10 | Train cukup besar dan test tetap terpisah |
| Threshold emergency | 0,80 | Kandidat emergency tingkat menengah |
| High-confidence threshold | 0,85 | Satu chunk dapat langsung memicu; selain itu butuh dua chunk |

## 4. Timeline & Milestones

### Week 13

| Waktu | Aktivitas | Output |
|---|---|---|
| Senin | Finalisasi masalah, scope, sumber data, risiko | Proposal dan risk register |
| Rabu | Audit data, cleaning, label, split, EDA | Dataset final dan EDA |
| Jumat | Baseline, IndoBERT, metrik, error analysis | Experiment log dan model candidate |

### Week 14

| Waktu | Aktivitas | Output |
|---|---|---|
| Senin | Integrasi FastAPI, ZKP, Whisper, model, database | API dan pipeline end-to-end |
| Rabu | Dashboard, firmware, tests, laporan, model card | Demo candidate dan dokumentasi |
| Jumat | Presentasi, demo/video cadangan, Q&A | Final submission |

### Milestone Status

| Milestone | Status |
|---|---|
| Proposal, dataset, EDA | Selesai/didokumentasikan |
| 4 baseline + IndoBERT comparison | Selesai pada dokumentasi ini |
| 5-fold CV baseline | Selesai |
| Fine-tuned IndoBERT tersimpan | Selesai |
| FastAPI/dashboard/firmware | Selesai sebagai prototipe |
| Docker | Belum selesai |
| Uji lapangan, noise, mask, replay, network loss | Belum selesai |
| Video demonstrasi final | Belum diverifikasi |

## 5. Risk Assessment

| Risiko | Prob. | Dampak | Severity | Mitigasi |
|---|---|---|---|---|
| Kebisingan industri merusak STT | Tinggi | Kritis | Kritis | Dataset noise nyata, directional mic, VAD, augmentasi SNR, fallback tombol |
| Masker/respirator menurunkan kejelasan | Tinggi | Tinggi | Kritis | Uji bermasker per jarak/SNR dan kalibrasi threshold |
| Emergency terlewat (FN) | Sedang | Kritis | Kritis | Optimalkan recall/PR curve, threshold, multimodal trigger, human escalation |
| Alarm palsu | Sedang | Tinggi | Tinggi | Negation test, two-chunk policy, konfirmasi petugas, audit error |
| Replay audio/perangkat palsu | Sedang | Kritis | Kritis | TLS, nonce, audio hash/message binding, counter/timestamp, secure storage |
| Wi-Fi/server terputus | Tinggi | Kritis | Kritis | Local fallback alarm, retry queue, watchdog, health monitoring |
| Latency Whisper CPU tinggi | Sedang | Tinggi | Tinggi | Benchmark, warm-up, quantization, edge/server sizing, streaming |
| Konflik/overlap data | Sedang | Tinggi | Tinggi | Dedup berdasarkan teks sebelum split, adjudikasi label, group split |
| Bias domain/sumber | Sedang | Tinggi | Tinggi | Simpan provenance dan evaluasi per kelompok noise/speaker |
| Kebocoran audio/PII | Sedang | Kritis | Kritis | TLS, encryption at rest, RBAC, retention policy, consent |
| Scope terlalu lebar | Tinggi | Tinggi | Tinggi | Pisahkan MVP ML, security prototype, dan evaluasi lapangan |
| Kredensial firmware bocor | Tinggi | Kritis | Kritis | Hapus secret dari source/history, provisioning/NVS, rotasi credential |

## 6. Expected Deliverables

### Deliverable teknis

- Dataset final dan notebook fine-tuning.
- Model IndoBERT tersimpan beserta tokenizer dan metadata.
- Backend FastAPI, database SQLite, dashboard monitoring, dan Telegram opsional.
- Firmware ESP32-S3 + INMP441 + LED + buzzer.
- Autentikasi Schnorr, token upload, dan server proof.
- Test suite otomatis.

### Deliverable dokumentasi

- Proposal, EDA report, experiment report, model card, technical report.
- Worksheet 1–12 dan rubric self-assessment.
- Panduan menjalankan, struktur presentasi, demo, Q&A, dan checklist.

## 7. Resources & Tools

| Kelompok | Resource |
|---|---|
| Hardware | ESP32-S3, INMP441, LED, buzzer, laptop/server |
| ML/NLP | PyTorch, Transformers, IndoBERT, faster-whisper, scikit-learn |
| Backend | FastAPI, Uvicorn, SQLAlchemy, Pydantic, SQLite |
| Firmware | Arduino IDE, ArduinoJson, ESP32 board package |
| Testing | pytest, TestClient/httpx |
| Monitoring | Dashboard HTML/CSS/JS dan Telegram |
| Version control | Git/GitHub |

## 8. Approval & Sign-Off

**Disusun oleh:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Status mahasiswa:** Proposal telah diisi berdasarkan implementasi aktual.  
**Persetujuan dosen:** Menunggu penilaian/persetujuan pengajar.

## References

1. International Labour Organization, “Safety and health at work.”
2. L. H. Arnal et al., “Human screams occupy a privileged niche in the communication soundscape,” *Current Biology*, 2015, <https://doi.org/10.1016/j.cub.2015.06.043>.
3. M. Vlachos et al., “A robust end-to-end IoT system for supporting workers in mining industries,” *Sensors*, 2024, <https://doi.org/10.3390/s24113317>.
4. B. Wilie et al., “IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding,” AACL-IJCNLP, 2020, <https://aclanthology.org/2020.aacl-main.85/>.
5. J. Devlin et al., “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,” 2018, <https://doi.org/10.48550/arXiv.1810.04805>.
6. A. Radford et al., “Robust Speech Recognition via Large-Scale Weak Supervision,” 2022, <https://doi.org/10.48550/arXiv.2212.04356>.

