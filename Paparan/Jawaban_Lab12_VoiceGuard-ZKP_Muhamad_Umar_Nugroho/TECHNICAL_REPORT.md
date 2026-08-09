# Technical Report: VoiceGuard-ZKP

**Sistem IoT Cerdas untuk Deteksi Kondisi Darurat Berbasis Suara dengan Autentikasi Zero-Knowledge Proof**

**Nama:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Tahun akademik:** 2025/2026

## Abstract

VoiceGuard-ZKP adalah prototipe pendukung keselamatan yang menangkap audio pekerja melalui ESP32-S3 dan INMP441, mengautentikasi perangkat dengan Schnorr Zero-Knowledge Proof, mentranskripsikan suara memakai faster-whisper Small, lalu mengklasifikasikan teks sebagai Normal atau Emergency memakai IndoBERT dan aturan bahasa. Dataset final terdiri dari 54.656 teks bahasa Indonesia yang hampir seimbang. Fine-tuned IndoBERT mencapai accuracy 90,61%, precision Emergency 92,25%, recall Emergency 88,12%, dan F1 Emergency 90,14% pada held-out test set. Backend FastAPI menyimpan event, menyediakan dashboard identitas/lokasi/transkrip, mengirim notifikasi Telegram, dan mengembalikan server proof serta keputusan buzzer. Seluruh 34 automated tests lulus. Meski prototipe menunjukkan kelayakan teknis, ia belum membuktikan robustness pada noise industri, masker, replay, perangkat palsu, kehilangan jaringan, dan latency audio-ke-alert. ZKP hanya membuktikan pengetahuan secret perangkat dan tidak menggantikan TLS, integritas stream, atau anti-replay.

**Keywords:** emergency detection, IndoBERT, Whisper, IoT, ESP32-S3, Schnorr, Zero-Knowledge Proof, occupational safety.

## 1. Executive Summary

Masalah yang dibahas ialah keterlambatan pengenalan kondisi darurat ketika korban tidak mampu mengakses perangkat komunikasi dan hanya dapat memberi respons verbal. VoiceGuard-ZKP menambahkan kanal suara hands-free yang menghubungkan device, lokasi, ML, dan alert. Sistem tidak ditujukan menggantikan tombol darurat, radio, CCTV, prosedur K3, atau petugas.

Hasil utama:

- Dataset: 54.656 teks, 51,34% Normal dan 48,66% Emergency.
- IndoBERT: test accuracy 90,61% dan F1 Emergency 90,14%.
- Error: 197 false positive dan 316 false negative.
- Implementasi: firmware, API, database, dashboard, ZKP demo, STT, classifier, notifikasi, buzzer.
- Verification: 34/34 automated tests lulus.
- Gap: Docker, real-time streaming sejati, security production, real-audio field benchmark, dan end-to-end latency belum selesai.

Rekomendasi prioritas adalah meningkatkan recall Emergency dengan data audio industri, membersihkan konflik label, menyamakan konfigurasi tokenisasi training/inference, menerapkan TLS+audio message binding+anti-replay, dan menambahkan local fail-safe saat jaringan gagal.

## 2. Introduction

### 2.1 Background

Kecelakaan kerja dapat menghambat korban untuk menyentuh telepon atau alarm. Suara dipilih karena dapat diberikan tanpa tangan dan karena jeritan memiliki karakteristik akustik yang menarik perhatian. Namun alasan ini tidak berarti suara selalu unggul: pabrik memiliki noise, pekerja dapat memakai masker/respirator, dan korban mungkin tidak mampu berbicara. Karena itu, VoiceGuard-ZKP menggunakan suara sebagai kanal tambahan.

IoT memungkinkan sensor mengirim event, identitas perangkat, dan lokasi ke dashboard. Machine learning diperlukan karena variasi ujaran tidak cukup ditangani daftar kata statis. Keamanan diperlukan karena alert dari perangkat palsu dapat mengganggu operasi. Ketiga kebutuhan tersebut membentuk arsitektur gabungan device–server–ML–dashboard.

### 2.2 Research Questions

1. Bagaimana menangkap suara pekerja dalam format yang dapat diproses model?
2. Bagaimana mentranskripsikan bahasa Indonesia dan menangani error ASR?
3. Seberapa baik IndoBERT membedakan Normal dan Emergency?
4. Bagaimana membuktikan perangkat terdaftar tanpa mengirim secret?
5. Bagaimana menyajikan lokasi, transkrip, dan alert secara terpadu?
6. Apa batas keamanan, latency, reliability, dan validitas bukti saat ini?

### 2.3 Contributions

- Dataset klasifikasi teks bahasa Indonesia yang terintegrasi.
- Fine-tuned IndoBERT dua kelas dan pembanding TF-IDF.
- Pipeline audio dengan filter aktivitas, STT, koreksi alias, classifier, dan policy trigger.
- Prototipe device authentication Schnorr dan signed upload token.
- Dashboard hijau/merah yang menampilkan identitas, lokasi, transkrip, dan confidence.
- Dokumentasi keterbatasan serta roadmap pengujian produksi.

## 3. Literature Review

### 3.1 Voice as an Emergency Signal

Arnal et al. menunjukkan jeritan manusia menempati area khusus pada soundscape komunikasi dan memiliki temporal roughness yang berhubungan dengan respons terhadap bahaya. Temuan ini mendukung potensi suara sebagai sinyal, tetapi tidak membuktikan bahwa keyword classifier akan selalu bekerja di industri. Validasi aplikasi tetap memerlukan rekaman domain nyata.

### 3.2 IoT for Worker Safety

Sistem IoT keselamatan menghubungkan sensor, jaringan, pemrosesan, dan pusat monitoring. Kajian dan implementasi pada lingkungan seperti konstruksi/mining menunjukkan nilai integrasi, tetapi juga menyoroti reliability jaringan, latency, harsh environment, dan kebutuhan fail-safe. VoiceGuard-ZKP menempatkan ML server-side untuk menjaga firmware sederhana, dengan trade-off ketergantungan jaringan.

### 3.3 Whisper

Whisper adalah model speech recognition yang dilatih dalam skala besar pada data multibahasa. Proyek menggunakan faster-whisper Small berbasis CTranslate2, bahasa `id`, beam size 5, CPU float32. Whisper mengubah audio menjadi teks; ia bukan classifier Emergency. Error Whisper dapat menjadi input salah bagi IndoBERT, sehingga metrik classifier teks tidak mewakili keseluruhan pipeline.

### 3.4 BERT and IndoBERT

BERT memakai self-attention dua arah untuk membangun representasi kontekstual. IndoBERT/IndoNLU menyediakan model dan benchmark bahasa Indonesia. Fine-tuning menambahkan classifier dua kelas pada representasi `[CLS]` dan memperbarui bobot encoder dengan data proyek. Dibanding TF-IDF, IndoBERT dapat membedakan konteks seperti negasi, tetapi tetap rentan pada domain shift dan kalimat yang tidak terwakili.

### 3.5 Zero-Knowledge Proof and Schnorr

Konsep zero-knowledge diperkenalkan oleh Goldwasser, Micali, dan Rackoff pada 1985. Protokol identifikasi Schnorr diperkenalkan Claus-Peter Schnorr pada akhir 1980-an. ZKP memungkinkan prover meyakinkan verifier bahwa ia mengetahui secret tanpa mengirim secret itu.

Tiga properti konseptual:

- **Completeness:** prover jujur dengan secret valid diterima.
- **Soundness:** pihak tanpa secret sulit meyakinkan verifier.
- **Zero-knowledge:** verifier tidak mempelajari secret dari interaksi.

VoiceGuard-ZKP menggunakannya untuk identitas perangkat, bukan kerahasiaan audio.

## 4. Methodology

### 4.1 R&D Method

Metode Research and Development dipilih karena hasil penelitian berupa prototipe terpadu. Tahap proyek:

1. Identifikasi masalah dan stakeholder.
2. Penetapan scope dan success metrics.
3. Integrasi, cleaning, dan audit data.
4. Pengembangan baseline dan IndoBERT.
5. Pengembangan firmware, autentikasi, API, database, dan dashboard.
6. Integration testing dan evaluasi.
7. Review limitation, keamanan, dan revisi.

### 4.2 Problem Formulation

Untuk dataset \(D=\{(x_i,y_i)\}_{i=1}^{N}\), \(x_i\) adalah teks dan \(y_i\in\{0,1\}\), dengan 0=Normal dan 1=Emergency. Model \(f_\theta\) menghasilkan probabilitas:

\[
\hat{p}_i=P(y_i=1\mid x_i;\theta)
\]

Training meminimalkan binary/multiclass cross-entropy atas dua logits:

\[
\mathcal{L}(\theta)=-\frac{1}{N}\sum_i\sum_{k\in\{0,1\}}\mathbf{1}[y_i=k]\log P(y_i=k\mid x_i;\theta)
\]

Pada runtime, label model tidak selalu sama dengan keputusan alarm. Policy sistem mempertimbangkan keyword override dan confidence/chunk history.

### 4.3 Data Pipeline

Paparan mendokumentasikan MEDISCO, IndSpeech/TelDialog, SVCSR/ASR-IndoCSC, dan HumAID. Data digabung, dibersihkan, ditambah contoh negasi, diseimbangkan, dan dilabeli. Dataset final tidak memiliki kolom provenance, sehingga urutan transformasi per sampel tidak dapat direplikasi sepenuhnya.

Audit final:

- 54.656 baris; missing=0; empty=0; full duplicate=0.
- 13 teks memiliki label bertentangan.
- Normal 28.058; Emergency 26.598.
- Rata-rata 13,21 kata; maksimum 73 kata.

### 4.4 Data Split

```python
train_df, temp_df = train_test_split(
    working_df, test_size=0.2,
    stratify=working_df["label"], random_state=42
)
valid_df, test_df = train_test_split(
    temp_df, test_size=0.5,
    stratify=temp_df["label"], random_state=42
)
```

Hasil: train 43.724, validation 5.466, test 5.466. Stratification mempertahankan kelas; random state membuat split konsisten. Ditemukan tiga overlap teks antarsplit sehingga dedup-before-split menjadi revisi wajib.

### 4.5 Baseline Models

Baseline memakai TF-IDF unigram+bigram maksimal 50.000 fitur, yang di-fit hanya pada train. Model: Dummy, Logistic Regression, LinearSVC, dan MultinomialNB. LinearSVC dituning pada `C={0,25;0,5;1;2}` dan divalidasi lima fold.

### 4.6 IndoBERT Training

| Parameter | Nilai |
|---|---|
| Base model | `indobenchmark/indobert-base-p1` |
| Max length | 64 |
| Batch size | 8 |
| Epoch | 1 |
| Learning rate | 2e-5 |
| Optimizer | AdamW |
| Encoder frozen | Tidak |
| Seed | 42 |

Max length 64 dipilih karena ujaran relatif pendek dan resource terbatas. Satu epoch membatasi biaya komputasi, tetapi belum membuktikan konfigurasi optimal.

### 4.7 Evaluation Metrics

Dengan TP, TN, FP, dan FN:

\[
Accuracy=\frac{TP+TN}{TP+TN+FP+FN}
\]

\[
Precision_E=\frac{TP}{TP+FP},\quad Recall_E=\frac{TP}{TP+FN}
\]

\[
F1_E=2\cdot\frac{Precision_E\cdot Recall_E}{Precision_E+Recall_E}
\]

Recall Emergency adalah metrik keselamatan utama karena FN berarti bahaya terlewat. Precision tetap penting untuk mencegah alarm fatigue.

## 5. System Architecture

### 5.1 Data Flow

```text
Pekerja
  ↓ suara
INMP441 → ESP32-S3 → Schnorr authentication → HMAC upload token
                                               ↓
                                      POST /api/process/audio
                                               ↓
                  simpan WAV → activity filter → faster-whisper
                                               ↓ teks
                   autocorrect reviewed aliases → IndoBERT + rules
                                               ↓
                    SQLite → dashboard/Telegram → server proof
                                               ↓
                                      response → buzzer
```

### 5.2 Hardware

- INMP441: microphone digital I2S.
- ESP32-S3: capture dan networking.
- LED GPIO12: indikator capture.
- Buzzer GPIO9: indikator Emergency.
- Format audio: PCM WAV mono, 16-bit, 16 kHz, chunk 3 detik.

### 5.3 Audio Preprocessing and STT

Backend menghapus DC offset, high-pass/low-pass sederhana, mengukur level frame 20 ms, lalu menolak audio bila p90 terlalu rendah, rasio signal/noise di bawah threshold, atau active ratio kurang. Audio dinormalisasi ke target RMS sebelum Whisper. Whisper juga memiliki filter no-speech probability, log probability, compression ratio, dan detector repetisi.

### 5.4 Autocorrect

Autocorrect bukan model Random Forest atau ML baru. Ia adalah dictionary mapping alias ASR yang telah direview, dibantu perhitungan Levenshtein untuk pencatatan jarak. Kata di luar mapping dibiarkan agar nama/kata valid tidak diubah agresif. Contoh: distorsi `tolon` dikembalikan menjadi `tolong`.

### 5.5 Hybrid Emergency Policy

1. IndoBERT menghasilkan label dan confidence.
2. Keyword/negation rule dapat memaksa Emergency pada istilah kuat tanpa negasi.
3. Jika confidence Emergency ≥0,85, satu chunk memicu alert.
4. Jika 0,80≤confidence<0,85, diperlukan dua chunk Emergency berurutan.
5. Jika <0,80 atau label Normal, notifikasi tidak dipicu.

Policy ini merupakan guardrail, tetapi metrik IndoBERT murni tidak boleh diklaim sebagai metrik sistem hibrida.

### 5.6 Schnorr Authentication

Parameter demo: \(p=23,q=11,g=2\). Perangkat memiliki secret \(x\), public key \(y=g^x\bmod p\). Protokol:

1. Prover memilih nonce acak \(r\) dan mengirim commitment \(t=g^r\bmod p\).
2. Server mengirim challenge \(c\).
3. Prover mengirim \(s=(r+cx)\bmod q\).
4. Server menerima bila:

\[
g^s\bmod p=(t\cdot y^c)\bmod p
\]

Karena \(g^{r+cx}=g^r(g^x)^c=t y^c\), prover yang mengetahui \(x\) dapat menjawab tanpa mengirim \(x\).

Setelah valid, server menerbitkan token HMAC bertanda tangan dengan TTL. Server proof memakai Fiat–Shamir dan terikat pada string device/audio/label/confidence. Namun proof autentikasi device tidak mengikat hash audio yang diupload; HTTP default juga tidak mengenkripsi audio.

### 5.7 Backend and Dashboard

FastAPI memisahkan routers, services, repositories, schemas, database models, dan exception handling. Endpoint inti mencakup health, devices, auth challenge/verify, authenticated audio processing, monitoring overview/events, dan dashboard. Dashboard membaca event terbaru setiap detik dan mengubah keadaan hijau/merah, sekaligus menampilkan identitas perangkat, lokasi, transkrip, dan confidence.

## 6. Results

### 6.1 Model Comparison

| Model | Evaluation | Accuracy | Recall E | F1 E |
|---|---|---:|---:|---:|
| Dummy | Validation | 0,5134 | 0 | 0 |
| Logistic Regression | Validation | 0,8802 | 0,8395 | 0,8721 |
| LinearSVC C=0,25 | Test | 0,8932 | 0,8586 | 0,8866 |
| IndoBERT | Test | **0,9061** | **0,8812** | **0,9014** |

Detail lengkap tersedia pada [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md).

### 6.2 Confusion Matrix

IndoBERT menghasilkan TN=2.609, FP=197, FN=316, TP=2.344. Accuracy:

\[
\frac{2609+2344}{5466}=0,906147
\]

Precision Emergency:

\[
\frac{2344}{2344+197}=0,922471
\]

Recall Emergency:

\[
\frac{2344}{2344+316}=0,881203
\]

### 6.3 Cross-Validation

5-fold LinearSVC memberi mean accuracy 0,8863±0,0021 dan F1 0,8793±0,0023. Stabilitas ini menunjukkan baseline kuat. IndoBERT belum divalidasi lintas fold/seed.

### 6.4 Tests and Latency

- Automated tests: 34 passed in 42,76 seconds.
- Cakupan fungsi: API, dashboard routes, token tampering, ZKP valid/invalid, quiet audio, autocorrect, keyword override, negasi, threshold policy, pipeline persistence.
- Warmed IndoBERT CPU: mean 50,57 ms pada 10 input lokal.
- Real Whisper + real microphone + network + Telegram latency: belum dibenchmark end-to-end.

## 7. Analysis and Discussion

### 7.1 Why IndoBERT Performed Better

IndoBERT dapat menggunakan urutan dan konteks subword, sedangkan TF-IDF terutama melihat frekuensi kata/ngram. Hal ini memberi peningkatan test F1 sekitar 1,47 points atas tuned LinearSVC. Namun peningkatan relatif kecil dibanding kenaikan ukuran/kompleksitas, sehingga baseline tetap relevan untuk perangkat resource terbatas.

### 7.2 Error Priority

False negative menyumbang 61,60% dari seluruh kesalahan IndoBERT. Untuk sistem keselamatan, pengembangan harus mengutamakan recall, lalu mengontrol false alarm dengan policy dua chunk dan konfirmasi manusia. Accuracy saja dapat menutupi risiko tersebut.

### 7.3 ML Model vs System Behavior

Smoke test menunjukkan beberapa frasa jelas dapat diprediksi Normal oleh IndoBERT murni, sementara pipeline penuh memaksa Emergency melalui keyword. Ini memperlihatkan pentingnya membedakan:

- metrik classifier pada teks ground truth;
- metrik classifier pada transkrip Whisper;
- metrik sistem hibrida setelah rules;
- metrik operasional audio-ke-alert.

Keempatnya belum diukur bersama dalam satu benchmark.

### 7.4 Data Validity

Kelas seimbang dan missing=0 adalah kekuatan. Konflik label, overlap kecil, serta hilangnya provenance adalah kelemahan. Klaim SMOTE juga tidak dapat diaudit dari final CSV; karena data sudah seimbang, versi berikutnya sebaiknya fokus pada coverage condition daripada oversampling.

### 7.5 Security Interpretation

ZKP memberikan authentication evidence, bukan confidentiality, integrity, availability, atau freshness seluruh stream. Secure design memerlukan:

- TLS untuk confidentiality/integrity in transit;
- audio hash + device ID + timestamp + counter untuk message binding;
- nonce/challenge one-time dan replay cache;
- parameter/curve produksi serta library diaudit;
- secret provisioning/rotation dan secure storage;
- rate limit, authorization, logging, dan incident response.

### 7.6 Reliability

Firmware melakukan capture 3 detik lalu upload dan menunggu hasil. Ini near-continuous chunk processing, bukan streaming real-time penuh. Gangguan selama proses server dapat menciptakan blind window atau latency tinggi. Local fallback dan buffering dibutuhkan.

## 8. Deployment and Production Considerations

### 8.1 Current State

Backend dapat dijalankan dengan Uvicorn dan memiliki Swagger, health route, dashboard, dan SQLite. Model dimuat saat startup bila `PRELOAD_ML_MODELS=true`. Artefak Whisper dan IndoBERT tersedia lokal. Dockerfile belum ada.

### 8.2 Configuration Risks

- Training max length 64 vs inference max length 512 harus disamakan.
- Beberapa dependencies belum pinned.
- Source firmware menyimpan credential jaringan; harus dihapus/dirotasi.
- Demo placeholder audio di service dapat menghasilkan dummy Emergency dan harus dihapus atau dibatasi hanya pada test environment.
- SQLite cocok untuk demo, bukan concurrency/HA tinggi.

### 8.3 Monitoring and SLA

SLA kandidat harus ditetapkan setelah benchmark:

- end-to-end latency p50/p95/p99;
- uptime server dan device heartbeat;
- notification delivery success;
- per-condition recall/false alarm;
- authentication failure/replay count;
- queue/retry and dropped chunks;
- model/data drift.

## 9. Threat Model

| Threat | Current control | Gap |
|---|---|---|
| Unknown device | Registered public key + Schnorr | Demo params, secret storage |
| Tampered auth token | HMAC-SHA256 + TTL | Secret rotation/secure storage |
| Reused challenge | Stored/marked used + expiry | Concurrency/race audit |
| Replayed audio | Tidak ada binding penuh | Timestamp/counter/audio hash |
| Eavesdropping | Tidak ada TLS default | HTTPS/mTLS |
| Fake alert text/audio | ML/rules only | Liveness/multimodal validation |
| DoS/upload flood | Basic endpoint protection | Rate limit, quota, WAF |
| Credential leak | `.env` ignored | Firmware still hardcoded |
| Database/audio theft | Local storage | Encryption/RBAC/retention |

## 10. Limitations

1. Bukan safety-certified system.
2. Belum diuji pada kondisi industri nyata.
3. Belum menguji pekerja bermasker/respirator.
4. Belum menguji replay, fake device, atau network loss.
5. Belum mengukur WER Whisper dan end-to-end latency.
6. Dataset tidak memiliki provenance/fairness attributes.
7. Konflik label dan overlap teks masih ada.
8. Docker, CI/CD, load test, dan monitoring produksi belum tersedia.
9. Parameter ZKP kecil dan HTTP belum secure channel.
10. Model hanya dua kelas dan bahasa Indonesia.

## 11. Development Roadmap

### Priority 0 — Safety and Security

- Hapus credential dari firmware dan rotasi.
- Hapus/guard `AUDIO_PLACEHOLDER` untuk test only.
- TLS/mTLS, audio-message binding, counter/timestamp, replay cache.
- Local alarm/fallback ketika server tidak terjangkau.

### Priority 1 — Evidence

- Test matrix noise × SNR × distance × mask × speaker × phrase.
- Ukur WER, keyword recall, system recall, false alarm/hour, latency p95.
- Simulasikan network loss, server restart, Telegram failure, and retry.
- Simpan prediction-level artifacts dan video demo.

### Priority 2 — Model/Data

- Adjudikasi 13 konflik dan dedup before split.
- Simpan provenance dan group-aware split.
- Fine-tune lebih dari satu konfigurasi/seed dan kalibrasi threshold.
- Tambah hard negatives, dialect/noise, masked speech, dan class severity.

### Priority 3 — Deployment

- Docker, PostgreSQL, object storage, queue, metrics, logs, alerts.
- Versioned model registry, CI/CD, rollback, and drift monitoring.
- Streaming/VAD yang terus memantau tanpa menunggu upload penuh.

## 12. Conclusion

VoiceGuard-ZKP membuktikan bahwa device, ZKP prototype, speech-to-text, IndoBERT, dashboard, lokasi, notifikasi, dan buzzer dapat dirangkai dalam satu prototipe. IndoBERT mencapai F1 Emergency 90,14% pada test teks, dan kode yang diuji melewati 34 automated tests. Hasil ini cukup untuk menunjukkan feasibility akademik, tetapi belum cukup untuk klaim siap industri. Recall Emergency, robustness audio, end-to-end latency, reliability jaringan, dan keamanan stream harus menjadi gate sebelum pilot lapangan.

## 13. References

1. International Labour Organization, “Safety and health at work,” <https://www.ilo.org/topics-and-sectors/safety-and-health-work>.
2. L. H. Arnal et al., “Human screams occupy a privileged niche in the communication soundscape,” *Current Biology*, 2015, <https://doi.org/10.1016/j.cub.2015.06.043>.
3. M. Vlachos et al., “A robust end-to-end IoT system for supporting workers in mining industries,” *Sensors*, 2024, <https://doi.org/10.3390/s24113317>.
4. B. Wilie et al., “IndoNLU,” AACL-IJCNLP, 2020, <https://aclanthology.org/2020.aacl-main.85/>.
5. J. Devlin et al., “BERT,” 2018, <https://doi.org/10.48550/arXiv.1810.04805>.
6. A. Radford et al., “Robust Speech Recognition via Large-Scale Weak Supervision,” 2022, <https://doi.org/10.48550/arXiv.2212.04356>.
7. S. Goldwasser, S. Micali, and C. Rackoff, “The Knowledge Complexity of Interactive Proof Systems,” 1985/1989.
8. C.-P. Schnorr, “Efficient Identification and Signatures for Smart Cards,” CRYPTO ’89.
9. M. Mitchell et al., “Model Cards for Model Reporting,” FAT* 2019, <https://doi.org/10.1145/3287560.3287596>.

