# EDA Report — VoiceGuard-ZKP

**Nama:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Dataset:** `dataset/dataset_final.csv`

## 1. Tujuan EDA

EDA dilakukan untuk memastikan dataset cukup besar, label hampir seimbang, teks tidak kosong, panjang teks sesuai batas tokenisasi, dan tidak terdapat pola kualitas data yang dapat menimbulkan leakage atau label ambiguity.

## 2. Data Dictionary

| Kolom | Tipe | Deskripsi | Contoh/Domain |
|---|---|---|---|
| `text` | string | Ujaran/kalimat bahasa Indonesia yang menjadi input model | Permintaan bantuan, bencana, atau kalimat normal |
| `label` | integer | Target numerik | 0=Normal, 1=Emergency |
| `label_name` | string | Nama target yang mudah dibaca | Normal/Emergency |

Unit analisis adalah satu teks, bukan satu file audio atau satu pembicara. Dataset final tidak menyimpan ID sumber, speaker, rekaman, noise, masker, perangkat, waktu, atau lokasi.

## 3. Dataset Overview

| Statistik | Nilai |
|---|---:|
| Baris | 54.656 |
| Kolom | 3 |
| Missing `text` | 0 |
| Missing `label` | 0 |
| Missing `label_name` | 0 |
| Teks kosong setelah trim | 0 |
| Full-row duplicates | 0 |
| Teks unik | 54.643 |
| Teks berulang tambahan | 13 |

### Distribusi kelas

| Label | Jumlah | Persentase |
|---|---:|---:|
| Normal (0) | 28.058 | 51,3356% |
| Emergency (1) | 26.598 | 48,6644% |
| Total | 54.656 | 100% |

Imbalance ratio minor/major adalah 26.598/28.058 = 0,9479. Dataset final praktis seimbang; accuracy masih dapat dipakai sebagai metrik sekunder, tetapi recall dan F1 Emergency tetap lebih relevan untuk keselamatan.

## 4. Univariate Analysis

### Panjang karakter

| Statistik | Karakter |
|---|---:|
| Rata-rata | 88,02 |
| Standar deviasi | 42,02 |
| Minimum | 1 |
| Q1 | 61 |
| Median | 80 |
| Q3 | 110 |
| P90 | 135 |
| P95 | 154 |
| P99 | 252 |
| Maksimum | 494 |

### Jumlah kata

| Statistik | Kata |
|---|---:|
| Rata-rata | 13,21 |
| Standar deviasi | 6,09 |
| Minimum | 1 |
| Q1 | 9 |
| Median | 12 |
| Q3 | 16 |
| P90 | 20 |
| P95 | 23 |
| P99 | 36 |
| Maksimum | 73 |

Rata-rata kelas Normal adalah 13,99 kata dan Emergency 12,39 kata. Emergency sedikit lebih pendek, masuk akal karena permintaan bantuan sering ringkas. Panjang teks dapat menjadi fitur diagnostik, tetapi tidak boleh dijadikan sinyal utama karena kalimat normal juga dapat pendek.

## 5. Bivariate Analysis

Hubungan utama adalah teks terhadap target. Karena input berupa teks, korelasi Pearson antarfitur numerik tidak relevan sebelum vectorization. Analisis yang tepat meliputi:

- distribusi panjang per label;
- keyword dan negasi per label;
- konflik teks identik antarkelas;
- evaluasi model pada subkelompok kalimat pendek/panjang;
- false positive dan false negative berdasarkan pola bahasa.

Temuan yang sudah terverifikasi: kelas hampir seimbang, Emergency rata-rata lebih pendek, dan 13 teks identik memiliki dua label berbeda.

## 6. Duplicate and Label Conflict Analysis

Tidak ada baris identik penuh, tetapi 13 teks muncul dua kali dengan label berlawanan. Contoh pola konflik mencakup ujaran sangat pendek/ambigu seperti “aduh”, “sakit”, “kenapa”, kalimat emosional seperti “ini mengerikan”, serta permintaan bantuan yang konteksnya tidak lengkap.

Implikasi:

1. Fungsi target tidak deterministik untuk teks tersebut; model menerima pengawasan yang saling bertentangan.
2. Split berbasis baris dapat menempatkan redaksi sama pada train dan validation/test.
3. Accuracy maksimal pada contoh ambigu menjadi tidak jelas tanpa pedoman anotasi.
4. Label perlu diadjudikasi berdasarkan konteks dan kebijakan keselamatan, bukan dibiarkan ganda.

Rekomendasi cleaning:

```text
normalize text
→ group by normalized_text
→ cari group dengan label.nunique() > 1
→ review manusia/pedoman anotasi
→ hapus atau tetapkan satu label
→ split setelah dedup dengan group-aware strategy
```

## 7. Split Analysis

| Split | Jumlah | Normal | Emergency | Persentase |
|---|---:|---:|---:|---:|
| Train | 43.724 | 22.446 | 21.278 | 80% |
| Validation | 5.466 | 2.806 | 2.660 | 10% |
| Test | 5.466 | 2.806 | 2.660 | 10% |

Strategi memakai `stratify` dan `random_state=42`, sehingga proporsi label stabil dan pembagian dapat direproduksi. Audit overlap menemukan:

- train ∩ validation: 2 teks;
- train ∩ test: 1 teks;
- validation ∩ test: 0 teks.

Walaupun overlap kecil, prosedur ideal ialah deduplikasi sebelum split dan menggunakan group split bila satu speaker/rekaman menghasilkan beberapa teks.

## 8. Missing Values, Outliers, and Validity

- Missing values dan teks kosong: tidak ada.
- “Outlier” panjang tidak otomatis dihapus karena kalimat panjang dapat sah.
- Hanya 1 teks melebihi pendekatan 64 kata, tetapi token subword bukan sama dengan kata. Distribusi token tokenizer perlu dihitung langsung untuk memastikan tingkat truncation sebenarnya.
- Maksimum 73 kata dapat terpotong oleh `max_length=64` token.
- Label_name perlu diverifikasi konsisten dengan label numerik; file saat audit konsisten secara struktur, tetapi aturan validasi eksplisit sebaiknya ditambahkan.

## 9. Provenance and Bias Audit

Paparan menyebut MEDISCO, IndSpeech/TelDialog, SVCSR/ASR-IndoCSC, dan HumAID. Namun CSV final hanya memiliki teks dan label. Akibatnya tidak dapat dihitung:

- kontribusi jumlah baris per sumber;
- train-test overlap berdasarkan sumber/speaker;
- performa per domain medis, percakapan, dan bencana;
- lisensi dan consent per sampel;
- proporsi teks terjemahan dibanding ujaran asli;
- performa per dialek, masker, gender, atau noise.

Tambahkan kolom `source_dataset`, `source_id`, `speaker_id`, `audio_id`, `language_origin`, `is_synthetic`, `noise_condition`, `mask_condition`, dan `annotation_version` pada dataset versi berikutnya.

## 10. Feature Engineering Candidates

| Fitur | Cara | Tujuan | Status |
|---|---|---|---|
| Token IndoBERT | Tokenizer subword | Representasi kontekstual | Aktif |
| Keyword count | Hitung istilah darurat | Guardrail recall | Aktif pada pipeline |
| Negation phrase | Deteksi “tidak/bukan/aman/latihan” | Kurangi false positive | Aktif pada aturan |
| Alias correction count | Jumlah koreksi reviewed | Audit error STT | Aktif/logged |
| Word/char length | Panjang teks | Diagnostik kualitas | EDA |
| Unique-word ratio | unik/total | Deteksi hallucination repetitif | Aktif |
| Dominant word/bigram | frekuensi maksimum | Deteksi repetisi | Aktif |
| STT no-speech probability | metadata Whisper | Tolak silence | Aktif sebagian |
| SNR/activity ratio | p90/noise floor | Tolak audio terlalu lemah | Aktif |
| Consecutive emergency | event sebelumnya per device | Stabilkan trigger | Aktif |

## 11. Five Key Insights

1. Dataset cukup besar dan hampir seimbang, sehingga imbalance bukan masalah utama versi final.
2. False negative lebih dominan daripada false positive pada model final.
3. Konflik label dan overlap teks adalah risiko data leakage kecil tetapi nyata.
4. Dataset teks tidak cukup untuk membuktikan robustness audio di pabrik.
5. Provenance yang hilang membatasi audit fairness, lisensi, dan generalisasi.

## 12. Modeling Decisions from EDA

- Gunakan stratified split dan primary metric recall/F1 Emergency.
- Pertahankan IndoBERT untuk konteks bahasa dan negasi.
- Gunakan guardrail keyword secara transparan, bukan menyebutnya performa model murni.
- Bersihkan konflik label sebelum retraining.
- Tambahkan evaluasi audio end-to-end dan per kondisi, bukan hanya test teks.
- Kalibrasi threshold pada validation set menggunakan PR curve serta biaya FN/FP.

## 13. Reproducibility

Statistik dihitung langsung dari `dataset/dataset_final.csv` pada 4 Agustus 2026. Split direplikasi dengan scikit-learn `train_test_split`, stratifikasi `label`, dan seed 42. Data mentah sumber dan skrip integrasi awal tidak seluruhnya tersedia di folder final, sehingga reproduksi dari sumber mentah sampai dataset final belum sepenuhnya tercapai.

