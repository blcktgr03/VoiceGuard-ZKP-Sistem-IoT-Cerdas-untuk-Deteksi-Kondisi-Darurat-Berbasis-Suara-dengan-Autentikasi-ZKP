# Model Card: VoiceGuard-ZKP IndoBERT Emergency Classifier v1.0

**Nama:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Tanggal dokumentasi:** 4 Agustus 2026

## 1. Model Overview

### 1.1 Purpose

Model mengklasifikasikan hasil transkripsi audio bahasa Indonesia ke kelas `Normal` atau `Emergency`. Model merupakan satu komponen dari pipeline VoiceGuard-ZKP; keputusan operasional akhir juga dipengaruhi filter audio, faster-whisper, autocorrect terbatas, aturan keyword/negasi, confidence threshold, dan histori chunk perangkat.

| Atribut | Nilai |
|---|---|
| Nama model | VoiceGuard-ZKP IndoBERT Emergency Classifier |
| Versi | 1.0 |
| Author | Muhamad Umar Nugroho |
| Base model | `indobenchmark/indobert-base-p1` |
| Task | Binary sequence classification |
| Label | 0=`Normal`, 1=`Emergency` |
| Framework | PyTorch + Hugging Face Transformers |
| Bahasa | Indonesia |
| Lisensi | Mengikuti lisensi model dasar dan masing-masing sumber data; perlu audit sebelum produksi |
| Lokasi artefak | `backend/bert/trained_model_indobert_full` |

### 1.2 Model Type & Architecture

IndoBERT adalah BERT yang telah dipralatih pada korpus bahasa Indonesia dan kemudian di-*fine-tune* penuh pada dataset proyek. Konfigurasi artefak menunjukkan:

| Komponen | Nilai |
|---|---:|
| Hidden layers | 12 |
| Hidden size | 768 |
| Attention heads | 12 |
| Intermediate size | 3.072 |
| Vocabulary | 50.000 token |
| Max position embeddings | 512 |
| Dropout | 0,1 |
| Output | 2 logits, kemudian softmax |
| Bobot model di disk | 497.795.072 byte |
| Total folder model | 498.506.398 byte |

Secara matematis, untuk token input \(x\), encoder menghasilkan representasi kontekstual token `[CLS]`, kemudian classifier membentuk logits \(z=W h_{CLS}+b\). Probabilitas kelas dihitung dengan:

\[
P(y=k\mid x)=\frac{e^{z_k}}{\sum_j e^{z_j}}
\]

Prediksi model murni adalah kelas dengan probabilitas terbesar. Pada pipeline sistem, hasil tersebut masih dapat dioverride oleh aturan keyword darurat yang telah ditinjau.

## 2. Intended Use

### 2.1 Primary Use Case

- Menyaring transkrip pendek bahasa Indonesia menjadi Normal atau Emergency.
- Membantu dashboard memprioritaskan event yang perlu dilihat petugas.
- Memicu notifikasi prototipe bila confidence/kebijakan chunk terpenuhi.
- Mendukung eksperimen akademik integrasi ML, IoT, dan autentikasi perangkat.

### 2.2 Out-of-Scope Uses

Model tidak boleh digunakan untuk:

- Menjadi satu-satunya sistem keselamatan atau dasar keputusan medis.
- Menentukan jenis cedera, tingkat keparahan, identitas pembicara, atau pelaku.
- Memantau pekerja secara diam-diam tanpa consent dan kebijakan retensi.
- Bahasa non-Indonesia atau dialek/lingkungan yang belum dievaluasi.
- Menjamin keamanan stream audio; hal itu bukan fungsi model maupun ZKP.
- Deployment produksi sebelum uji noise, masker, replay, network loss, latency, dan fairness.

### 2.3 Intended Users

- Petugas K3, supervisor, security, dan administrator sistem dalam skenario uji.
- Peneliti/mahasiswa yang mengevaluasi sistem darurat berbasis suara.
- Bukan untuk penggunaan otonom tanpa manusia dalam loop.

## 3. Factors

### 3.1 Relevant Factors

| Faktor | Potensi dampak |
|---|---|
| Kebisingan/SNR | Whisper salah transkripsi atau menolak audio |
| Masker/respirator | Artikulasi teredam, emergency dapat terlewat |
| Jarak dan arah mikrofon | Level suara dan intelligibility berubah |
| Aksen/dialek | Token/struktur berbeda dari data latih |
| Panjang ujaran | Truncation; training dibatasi 64 token |
| Negasi | “tidak ada kebakaran” dapat salah dianggap darurat |
| Kata pendek/ambigu | “aduh”, “sakit”, atau “api” perlu konteks |
| Error STT | Typo/alias mengubah makna sebelum klasifikasi |
| Domain data | Teks sosial/media berbeda dari ucapan pabrik |
| Repetisi/hallucination | Whisper dapat menghasilkan kata berulang saat sinyal buruk |

### 3.2 Factor Analysis Status

- Analisis kelas dan panjang teks: **tersedia**.
- Analisis per speaker, gender, dialek, kelompok umur: **tidak dapat dilakukan**, metadata tidak tersedia.
- Analisis per SNR/noise, masker, jenis mikrofon: **belum dilakukan**.
- Analisis konflik label: **dilakukan**, ditemukan 13 teks konflik.
- Analisis negasi: contoh dan unit test tersedia, tetapi benchmark khusus negasi belum tersedia.

## 4. Performance

### 4.1 Training Data

| Split | Total | Normal | Emergency |
|---|---:|---:|---:|
| Train | 43.724 | 22.446 | 21.278 |
| Validation | 5.466 | 2.806 | 2.660 |
| Test | 5.466 | 2.806 | 2.660 |
| Total | 54.656 | 28.058 | 26.598 |

Split dilakukan dua tahap dengan `stratify` dan `random_state=42`. Audit menemukan overlap teks unik train-validation sebanyak 2 dan train-test sebanyak 1 karena konflik/duplikasi teks. Nilainya kecil, tetapi proses yang lebih kuat harus melakukan deduplikasi/adjudikasi **sebelum** split.

### 4.2 Performance Metrics

#### 4.2.1 Overall Performance

| Metrik held-out test | Nilai |
|---|---:|
| Accuracy | 0,906147 |
| Macro precision | 0,907219 |
| Macro recall / balanced accuracy | 0,905498 |
| Macro F1 | 0,905926 |
| Weighted F1 | 0,906048 |
| MCC | 0,812715 |
| Validation F1 terbaik | 0,887175 |

#### 4.2.2 Per-Class Performance

| Kelas | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Normal | 0,891966 | 0,929793 | 0,910487 | 2.806 |
| Emergency | 0,922471 | 0,881203 | 0,901365 | 2.660 |

#### 4.2.3 Confusion Matrix

| Aktual \ Prediksi | Normal | Emergency |
|---|---:|---:|
| Normal | 2.609 (TN) | 197 (FP) |
| Emergency | 316 (FN) | 2.344 (TP) |

Turunan penting:

- False alarm rate = \(197/2806=7,02\%\).
- Miss rate = \(316/2660=11,88\%\).
- Total error = 513; false negative menyumbang \(316/513=61,60\%\) error.

### 4.3 Evaluation Methodology

- Split 80/10/10 dengan stratifikasi.
- Seed Python, NumPy, dan PyTorch = 42.
- Fine-tuning penuh selama satu epoch, batch size 8, learning rate `2e-5`.
- Checkpoint terbaik dipilih dari validation F1.
- Evaluasi akhir satu kali pada held-out test set.
- IndoBERT belum diuji dengan 5-fold CV karena biaya komputasi; 5-fold CV dilakukan pada baseline LinearSVC.
- ROC-AUC/PR-AUC IndoBERT tidak tersimpan karena output probabilitas test tidak dipersistenkan.

### 4.4 Business/Safety Interpretation

Precision Emergency 92,25% berarti sebagian besar alert teks yang dibuat model memang berasal dari label Emergency pada test set. Recall Emergency 88,12% berarti sekitar 12 dari 100 teks Emergency dapat terlewat. Untuk konteks keselamatan, angka tersebut belum cukup menjadi satu-satunya mekanisme alarm.

Smoke test model murni juga menunjukkan sensitivitas terhadap redaksi: “Tolong, kaki saya tertimpa kardus.” dan “Ada kebakaran di ruang produksi.” pernah diprediksi Normal, sedangkan redaksi lebih pendek “tolong ada kebakaran di ruang produksi” diprediksi Emergency. Pipeline hibrida dapat mengoreksi beberapa kasus dengan keyword override, tetapi hal ini harus diuji sebagai sistem penuh.

## 5. Limitations & Biases

### 5.1 Known Limitations

1. Dataset final tidak menyimpan provenance, speaker, noise, masker, atau device.
2. Terdapat 13 teks konflik label dan 3 overlap teks antarsplit.
3. Satu epoch bukan hyperparameter tuning yang menyeluruh.
4. Training menggunakan `max_length=64`; service inferensi saat ini menggunakan `max_length=512`.
5. Accuracy teks tidak sama dengan keberhasilan audio-ke-alert karena error Whisper dapat berantai.
6. Aturan keyword dapat meningkatkan recall tetapi juga dapat menaikkan false alarm.
7. Threshold 0,80/0,85 belum dikalibrasi dengan PR curve dan biaya kesalahan.
8. Tidak ada evaluasi noise industri, masker, dialek, replay, atau perangkat palsu.
9. Tidak ada latency end-to-end, load test, atau reliability test.
10. Model dapat berubah perilaku pada kalimat pendek, ambigu, negasi baru, atau domain di luar data latih.

### 5.2 Fairness & Bias

Fairness demografis belum dapat dihitung karena data tidak memiliki atribut kelompok. Risiko bias yang relevan adalah bias bahasa/dialek, gaya bicara, intensitas suara, kondisi disabilitas, masker, dan kondisi lingkungan. Evaluasi berikutnya harus melaporkan recall/false alarm per kelompok dan memastikan kelompok dengan suara lebih lemah tidak menerima performa lebih buruk secara sistematis.

### 5.3 Failure Cases

| Failure case | Dampak | Mitigasi |
|---|---|---|
| Emergency diprediksi Normal | Alarm terlambat/tidak terkirim | Optimalkan recall, keyword guardrail, multimodal fallback |
| Normal diprediksi Emergency | Alarm fatigue | Negation set, dua chunk, operator confirmation |
| Whisper kosong/noise | Tidak ada input bermakna | VAD/filter, microphone placement, local alarm |
| Whisper hallucination berulang | False trigger | Repetition detector yang sudah ada + benchmark |
| Alias autocorrect salah | Makna berubah | Mapping hanya alias reviewed dan unit tests |
| Jaringan putus | Audio tidak sampai | Queue lokal, retry, watchdog, fallback buzzer |

## 6. Data & Preprocessing

### 6.1 Pipeline

1. Integrasi dataset menurut paparan.
2. Pembersihan teks kosong dan normalisasi label.
3. Penambahan contoh negasi untuk membedakan kata bahaya dari pernyataan aman.
4. Pemeriksaan keseimbangan kelas.
5. Stratified split 80/10/10.
6. Tokenisasi IndoBERT, truncation dan padding hingga 64 token.
7. Fine-tuning encoder serta classifier.

Catatan: paparan menyebut SMOTE. Dataset final sudah hampir seimbang; file yang tersedia tidak memberi provenance proses SMOTE per baris. Untuk teks mentah, SMOTE tidak boleh diterapkan langsung pada string dan tidak boleh dilakukan sebelum split karena menimbulkan leakage. Dokumentasi produksi harus memperjelas implementasinya atau menghapus klaim tersebut.

### 6.2 Data Privacy & Ethics

- Minimalkan penyimpanan audio dan pisahkan identitas personal dari device ID.
- Dapatkan persetujuan serta komunikasikan area perekaman.
- Terapkan TLS, encryption at rest, RBAC, audit log, dan retention/deletion policy.
- Jangan memakai rekaman untuk evaluasi kinerja pekerja di luar tujuan keselamatan.
- Sediakan mekanisme koreksi event dan pelaporan false alarm.

## 7. Deployment & Monitoring

### 7.1 Deployment Information

| Komponen | Implementasi |
|---|---|
| Model serving | FastAPI/PyTorch pada backend lokal |
| Device | ESP32-S3 + INMP441 |
| Database | SQLite via SQLAlchemy |
| Dashboard | HTML/CSS/JavaScript dari route FastAPI |
| Notifikasi | Telegram jika token/chat dikonfigurasi |
| Authentication | Schnorr demo + signed short-lived HMAC token |
| Container | Belum ada Dockerfile |

Inferensi IndoBERT setelah warm-up pada CPU rata-rata 50,57 ms (10 input lokal; median 51,37 ms). Waktu load awal untuk empat inferensi smoke test sekitar 14,24 detik. Angka ini tidak mencakup capture 3 detik, upload, Whisper, database, Telegram, dan jaringan.

### 7.2 Monitoring Strategy

Monitor minimal:

- Volume event dan rasio Emergency per perangkat/lokasi.
- Confidence distribution dan pergeseran dari baseline.
- False alarm serta missed emergency hasil adjudikasi petugas.
- Word error rate/cer/keyword recall Whisper pada sampel berlabel.
- Latency p50/p95/p99 per tahap dan end-to-end.
- Network failure, retry, queue depth, uptime, memory, dan CPU.
- Authentication failure, challenge replay, token tampering, dan device anomaly.
- Drift bahasa/noise dengan evaluasi periodik.

### 7.3 Model Updates & Maintenance

- Review mingguan selama pilot, kemudian bulanan setelah stabil.
- Retraining hanya dengan event yang telah dianotasi dan disetujui.
- Simpan versioned dataset, code commit, config, tokenizer, seed, dan metrics.
- Jalankan regression test untuk negasi, typo, emergency, noise, dan security.
- Rollback bila recall Emergency atau false alarm melewati batas.

## 8. Recommendation & Limitations

### 8.1 When to Use

Gunakan hanya sebagai prototipe/pilot terkendali dengan manusia dalam loop, fallback manual, jaringan yang dipantau, dan pemberitahuan jelas kepada pengguna.

### 8.2 Release Gate Sebelum Produksi

- Recall Emergency memenuhi target pada data audio industri nyata.
- Uji masker, jarak, dialek, SNR, replay, fake device, network loss selesai.
- TLS dan audio-message binding diterapkan.
- Parameter Schnorr produksi dan secret provisioning diaudit.
- Firmware bebas credential hardcoded.
- Docker/controlled deployment, monitoring, backup, serta incident response tersedia.
- Latency p95 audio-ke-alert memenuhi SLA.

## 9. References & Citations

1. B. Wilie et al., “IndoNLU,” AACL-IJCNLP 2020, <https://aclanthology.org/2020.aacl-main.85/>.
2. J. Devlin et al., “BERT,” 2018, <https://doi.org/10.48550/arXiv.1810.04805>.
3. A. Radford et al., “Robust Speech Recognition via Large-Scale Weak Supervision,” 2022, <https://doi.org/10.48550/arXiv.2212.04356>.
4. M. Mitchell et al., “Model Cards for Model Reporting,” FAT* 2019, <https://doi.org/10.1145/3287560.3287596>.

## 10. Sign-Off

**Prepared by:** Muhamad Umar Nugroho — 2322101943 — III RPKK  
**Technical reviewer:** Belum ditetapkan  
**Safety/security approval:** Belum diberikan  
**Deployment status:** Prototype; **not approved for production safety use**.

## Appendix A — Training Configuration

```text
base_model = indobenchmark/indobert-base-p1
max_length = 64
batch_size = 8
epochs = 1
learning_rate = 2e-5
freeze_bert_encoder = false
seed = 42
split = 80/10/10 stratified
```

## Appendix B — Tuning History

IndoBERT belum memiliki grid/random search terdokumentasi. Model final memakai satu konfigurasi penuh. Eksperimen tuning terpisah dilakukan pada baseline LinearSVC dengan `C ∈ {0,25; 0,5; 1; 2}`; `C=0,25` memberi validation F1 tertinggi 0,8761.

