# Panduan Upload ke GitHub

Panduan singkat untuk upload repo dengan rapi:

1. Pastikan `.gitignore` sudah aktif.
2. Pastikan `.env` dan seluruh `config.h` lokal tidak tampil sebagai file yang akan di-commit.
3. Pastikan bobot `model.safetensors` dan `model.bin` tidak masuk commit biasa karena ukurannya melebihi 100 MB.
4. Jalankan test dengan `python -m pytest -q`.
5. Periksa perubahan dengan `git status` dan `git diff --check`.
6. Jalankan `git add .` lalu periksa lagi dengan `git status`.
7. Commit, hubungkan remote GitHub, lalu jalankan `git push -u origin main`.

Bobot model dapat dibagikan terpisah melalui Git LFS atau GitHub Release. Jangan paksa memasukkannya ke riwayat Git biasa.

## Struktur yang Disarankan

```text
backend/
dataset/
frontend/docs/
  images/
  guides/
frontend/firmware/
backend/tests/
README.md
.gitignore
```

## File Visual

- `frontend/docs/images/dashboard.png`
- `frontend/docs/images/flowchart.png`
- `frontend/docs/images/prototype.jpg`
