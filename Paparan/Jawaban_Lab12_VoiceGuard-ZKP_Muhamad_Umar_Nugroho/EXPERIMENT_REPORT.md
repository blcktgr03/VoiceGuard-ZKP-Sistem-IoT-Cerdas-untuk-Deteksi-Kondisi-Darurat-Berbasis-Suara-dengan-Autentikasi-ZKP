# Experiment Report — VoiceGuard-ZKP

**Nama:** Muhamad Umar Nugroho  
**NPM:** 2322101943  
**Kelas:** III RPKK  
**Tanggal eksperimen verifikasi:** 4 Agustus 2026

## 1. Experimental Questions

1. Apakah model teks sederhana mampu melampaui tebakan kelas mayoritas?
2. Apakah IndoBERT memberi peningkatan yang berarti atas baseline TF-IDF?
3. Seberapa stabil baseline terbaik pada 5-fold cross-validation?
4. Jenis kesalahan apa yang paling berbahaya bagi sistem?
5. Apakah hasil model murni konsisten dengan perilaku pipeline hibrida?

## 2. Reproducible Setup

```text
dataset = dataset/dataset_final.csv
target = label (0 Normal, 1 Emergency)
split = 80% train, 10% validation, 10% test
stratify = label
random_state = 42
TF-IDF = lowercase, unigram+bigram, max_features=50,000,
         min_df=2, sublinear_tf=True
```

Untuk baseline, vocabulary TF-IDF hanya di-*fit* pada train set. Pemilihan `C` dilakukan pada validation set. Test set digunakan setelah parameter dipilih. Pada 5-fold CV, vectorizer ditempatkan dalam pipeline dan di-*fit* ulang pada tiap fold untuk mencegah leakage.

## 3. Validation Experiments

Shared TF-IDF fit/transform time adalah 1,861 detik pada CPU. Waktu training di bawah tidak termasuk waktu shared vectorization.

| Model | Hyperparameter | Accuracy | Precision E | Recall E | F1 E | ROC-AUC | Train time |
|---|---|---:|---:|---:|---:|---:|---:|
| Dummy most-frequent | kelas mayoritas | 0,5134 | 0,0000 | 0,0000 | 0,0000 | 0,5000 | 0,001 s |
| TF-IDF + Logistic Regression | C=1,0 | 0,8802 | 0,9074 | 0,8395 | 0,8721 | 0,9534 | 0,340 s |
| TF-IDF + LinearSVC | C=1,0 | 0,8729 | 0,8821 | 0,8526 | 0,8671 | 0,9474 | 0,271 s |
| TF-IDF + MultinomialNB | alpha=1,0 | 0,8439 | 0,9143 | 0,7496 | 0,8238 | 0,9358 | 0,010 s |

Interpretasi: seluruh model nyata melampaui dummy. Logistic Regression memberi validation F1 terbaik pada konfigurasi default ini. MultinomialNB memiliki precision tinggi, tetapi recall rendah sehingga kurang cocok sebagai alarm keselamatan.

## 4. Hyperparameter Tuning

LinearSVC dipilih untuk tuning ringan karena cepat dan memberi baseline teks yang kuat. Hanya parameter regularisasi `C` yang diuji; ini **belum** memenuhi tuning multidimensi ideal pada rubrik.

| C | Validation accuracy | Validation F1 E | Waktu fit |
|---:|---:|---:|---:|
| 0,25 | **0,8836** | **0,8761** | 0,141 s |
| 0,50 | 0,8794 | 0,8732 | 0,190 s |
| 1,00 | 0,8729 | 0,8671 | 0,270 s |
| 2,00 | 0,8648 | 0,8593 | 0,439 s |

`C=0,25` dipilih karena memberi F1 tertinggi. Nilai C lebih besar menurunkan generalisasi, menunjukkan regularisasi lebih kuat membantu.

## 5. Five-Fold Cross-Validation

Model: TF-IDF + LinearSVC (`C=0,25`)  
Strategi: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` pada train set.

| Fold | Accuracy | Precision E | Recall E | F1 E |
|---:|---:|---:|---:|---:|
| 1 | 0,8868 | 0,9121 | 0,8491 | 0,8795 |
| 2 | 0,8898 | 0,9140 | 0,8539 | 0,8829 |
| 3 | 0,8847 | 0,9072 | 0,8501 | 0,8777 |
| 4 | 0,8836 | 0,9084 | 0,8461 | 0,8762 |
| 5 | 0,8867 | 0,9078 | 0,8538 | 0,8800 |
| **Mean** | **0,8863** | **0,9099** | **0,8506** | **0,8793** |
| **Std** | **0,0021** | **0,0027** | **0,0030** | **0,0023** |

Mean train accuracy adalah 0,9492 dan mean CV accuracy 0,8863, sehingga gap 6,29 percentage points. Gap masih di bawah ambang 15% rubric, tetapi menandakan regularisasi dan data cleaning tetap penting. Variasi fold kecil, sehingga baseline relatif stabil.

## 6. Held-Out Test Comparison

| Model final | Accuracy | Precision E | Recall E | F1 E | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Tuned TF-IDF + LinearSVC | 0,8932 | 0,9165 | 0,8586 | 0,8866 | 0,9582 |
| Fine-tuned IndoBERT | **0,9061** | **0,9225** | **0,8812** | **0,9014** | Tidak tersimpan |

IndoBERT meningkatkan test accuracy sekitar **1,30 percentage points** dan F1 Emergency sekitar **1,47 points** atas tuned LinearSVC. Dibanding dummy, peningkatan accuracy absolut adalah sekitar 39,28 points; perbandingan F1 tidak informatif karena dummy tidak pernah memprediksi Emergency.

## 7. Confusion Matrices

### Tuned LinearSVC

| Aktual \ Prediksi | Normal | Emergency |
|---|---:|---:|
| Normal | 2.598 | 208 |
| Emergency | 376 | 2.284 |

### IndoBERT

| Aktual \ Prediksi | Normal | Emergency |
|---|---:|---:|
| Normal | 2.609 | 197 |
| Emergency | 316 | 2.344 |

IndoBERT mengurangi FP sebanyak 11 dan FN sebanyak 60 dibanding tuned LinearSVC pada test split yang sama.

## 8. IndoBERT Training Configuration

| Parameter | Nilai |
|---|---|
| Base model | `indobenchmark/indobert-base-p1` |
| Fine-tuning | Full encoder + classifier |
| Max length | 64 token |
| Batch size | 8 |
| Epoch | 1 |
| Learning rate | 2e-5 |
| Optimizer | AdamW |
| Seed | 42 |
| Best epoch | 1 |
| Best validation F1 | 0,887175 |

Waktu training IndoBERT tidak dicatat pada metadata/log yang tersedia sehingga tidak diisi dengan perkiraan.

## 9. Error Analysis

### False Positive

- Jumlah IndoBERT: 197.
- Persentase dari seluruh error: 38,40%.
- False alarm rate pada kelas Normal: 7,02%.
- Dugaan pola yang perlu diperiksa: kata bahaya dalam negasi, pembicaraan berita/latihan, kata emosional tanpa insiden, dan kalimat ambigu.

### False Negative

- Jumlah IndoBERT: 316.
- Persentase dari seluruh error: 61,60%.
- Miss rate pada kelas Emergency: 11,88%.
- Dugaan pola: ujaran singkat/ambigu, istilah jarang, redaksi tidak eksplisit, truncation, konflik label, dan domain mismatch.

Daftar prediksi test per baris tidak tersimpan, sehingga pola di atas adalah hipotesis yang harus dikonfirmasi dengan mengekspor `text`, `actual`, `predicted`, dan `confidence` pada evaluasi berikutnya.

## 10. Smoke Test Model Murni

Empat input diuji langsung melalui `TextClassificationService` pada CPU:

| Input | Prediksi | Confidence |
|---|---|---:|
| Tolong, kaki saya tertimpa kardus. | Normal | 0,6447 |
| Ada kebakaran di ruang produksi. | Normal | 0,7961 |
| Saya tidak membutuhkan bantuan. | Normal | 0,6530 |
| Semua aman dan pekerjaan berjalan normal. | Normal | 0,8969 |

Uji terpisah dengan “tolong ada kebakaran di ruang produksi” menghasilkan Emergency. Artinya, model sensitif pada variasi redaksi dan konteks. Pipeline penuh memiliki keyword override yang akan menandai kata seperti `tolong`, `tertimpa`, dan `kebakaran` sebagai Emergency, tetapi performa hybrid perlu dihitung tersendiri agar tidak dicampur dengan metrik IndoBERT murni.

## 11. Latency Microbenchmark

Setelah model warm-up, 10 inferensi IndoBERT lokal pada CPU menghasilkan:

| Statistik | Nilai |
|---|---:|
| Mean | 50,57 ms |
| Median | 51,37 ms |
| Minimum | 41,69 ms |
| Maksimum | 65,66 ms |

Ini bukan end-to-end latency. Capture audio saja memakan 3 detik, kemudian masih ada autentikasi, upload, preprocessing, Whisper, database, notifikasi, dan respons jaringan.

## 12. Model Selection Decision

IndoBERT dipilih sebagai model utama karena:

1. Test F1 dan recall Emergency lebih tinggi daripada baseline yang diuji.
2. Representasi kontekstual lebih sesuai untuk bahasa Indonesia dan negasi.
3. Model dapat diintegrasikan langsung dengan Transformers/PyTorch.

Trade-off:

- IndoBERT jauh lebih besar dan lebih sulit dijelaskan daripada TF-IDF.
- Keuntungan F1 atas LinearSVC hanya sekitar 1,47 points, sehingga baseline tetap berguna untuk fallback ringan.
- Sistem hibrida meningkatkan robustness praktis, tetapi harus dievaluasi secara terpisah agar klaim model tidak bias.

## 13. Required Next Experiments

1. Hapus konflik label dan overlap, lalu retrain semua model pada split baru.
2. Tuning IndoBERT pada learning rate, epoch, weight decay, warmup, threshold, dan class cost menggunakan validation/CV.
3. Simpan probabilities dan plot ROC serta Precision–Recall curve.
4. Benchmark model murni versus model+autocorrect versus model+rules.
5. Evaluasi audio end-to-end per SNR, masker, jarak, dialek, replay, dan network condition.
6. Laporkan WER/CER Whisper serta keyword recall, tidak hanya metrik classifier teks.

