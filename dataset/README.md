# Dataset dan Fine-Tuning

Folder ini menyimpan data final dan seluruh alat untuk melatih IndoBERT.

## Isi Folder

| File | Kegunaan |
|---|---|
| `dataset_final.csv` | Dataset final kelas Normal dan Emergency |
| `dataset.csv` | Data tambahan/awal yang dipertahankan sebagai referensi |
| `train_bert_final_dataset.ipynb` | Notebook preprocessing, visualisasi, training, dan evaluasi |
| `run_full_finetune_indobert.py` | Runner notebook tanpa batas timeout |
| `run_full_finetune_indobert.bat` | Runner Windows dengan output log |
| `*.log` | Riwayat proses training |

## Alur Data

```text
Empat sumber data
  -> penggabungan
  -> penerjemahan data Inggris
  -> cleaning dan normalisasi
  -> penambahan contoh negasi
  -> penyeimbangan kelas
  -> dataset_final.csv
  -> split train/validation/test
  -> full fine-tuning IndoBERT
  -> evaluasi
  -> model backend
```

Dataset final berisi teks dan label biner. Contoh negasi seperti "tidak darurat", "bukan keadaan darurat", dan "semua aman" membantu model membedakan penyebutan kata bahaya dari kondisi yang benar-benar darurat.

## Menjalankan

```powershell
python dataset\run_full_finetune_indobert.py
```

Pantau prosesnya:

```powershell
Get-Content dataset\full_finetune_indobert_runner.log -Wait
```

Notebook memakai path relatif terhadap root proyek agar tidak bergantung pada nama pengguna Windows.
