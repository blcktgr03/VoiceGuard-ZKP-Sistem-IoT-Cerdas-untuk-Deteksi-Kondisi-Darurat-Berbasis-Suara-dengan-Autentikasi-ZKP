# Panduan Menjalankan Proyek

## Backend

```bash
uvicorn backend.main:app --reload
```

## ESP8266

```bash
cd firmware/esp8266
pio run --target upload
pio device monitor
```

## Catatan

- Pastikan `.env` sudah terisi
- Pastikan `SERVER_BASE_URL` mengarah ke IP laptop
- Pastikan ESP8266 dan laptop ada di jaringan yang sama
