# Deployment and Testing — VoiceGuard-ZKP

**Nama:** Muhamad Umar Nugroho — **NPM:** 2322101943 — **Kelas:** III RPKK

## 1. Current Deployment Architecture

```text
ESP32-S3/INMP441
  ├─ POST /challenge or /api/auth/challenge
  ├─ POST /verify or /api/auth/verify
  └─ POST /api/process/audio + Bearer token
           ↓
FastAPI → SQLite → Whisper → autocorrect → IndoBERT/rules
           ├─ /api/monitoring/overview
           ├─ /api/monitoring/events
           ├─ /dashboard
           ├─ Telegram
           └─ server proof + result to ESP32 buzzer
```

## 2. Prerequisites

- Windows + PowerShell.
- Conda environment `tf-new` atau Python environment setara.
- Model lokal pada `backend/models/faster-whisper-small` dan `backend/bert/trained_model_indobert_full`.
- `.env` yang menunjuk database, upload/log directory, Whisper, dan IndoBERT.
- ESP32-S3 dan laptop pada Wi-Fi yang sama untuk demo device.

## 3. Run Backend

```powershell
cd "C:\Users\L E N O V O\Documents\Arduino\machine_learning"
& "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe" -m pip install -r requirements.txt
& "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Addresses:

| Service | URL |
|---|---|
| Dashboard | `http://localhost:8000/dashboard` |
| OpenAPI | `http://localhost:8000/docs` |
| Health | `http://localhost:8000/api/health` |
| API for device | `http://IP-LAPTOP:8000` |

## 4. Device Registration

Prototype configuration uses device public key 9 from secret 5 under demo parameters. Register through Swagger `POST /api/devices`; keep the secret only on the device. A `409` means the ID already exists.

## 5. Firmware

Upload `frontend/firmware/esp32_inmp441/esp32_inmp441_emergency_detector/esp32_inmp441_emergency_detector.ino`. Verify microphone pins SD=16, WS=17, SCK=18, LED=12, buzzer=9, and server IP. Do not commit real Wi-Fi secrets; source currently requires remediation and credential rotation.

## 6. Automated Test Result

Command:

```powershell
$env:TMP="$PWD\.tmp_pytest_lab12"
$env:TEMP=$env:TMP
& "$env:USERPROFILE\miniconda3\envs\tf-new\python.exe" -m pytest -q -p no:cacheprovider
```

**Result on 4 August 2026:** `34 passed in 42.76s`.

Covered behavior:

- health and OpenAPI routes;
- dashboard and monitoring routes;
- Schnorr accept/reject;
- auth token roundtrip/tampering;
- audio activity and quiet WAV rejection;
- Indonesian autocorrect and protected words;
- emergency keyword override and negation;
- high-confidence/two-consecutive-chunk policy;
- pipeline persistence, notification mock, and server proof.

Not covered as real integration:

- actual ESP32 network session;
- real microphone + real Whisper + real IndoBERT + Telegram in one test;
- industrial noise/mask/replay/network loss;
- concurrent devices, load, soak, or latency SLA;
- Docker/container behavior.

## 7. Endpoint Status

| Endpoint/capability | Status |
|---|---|
| `/api/health` | Implemented/tested |
| `/api/devices` | Implemented |
| `/api/auth/challenge` | Implemented |
| `/api/auth/verify` | Implemented |
| `/api/process/audio` | Implemented/protected |
| `/api/monitoring/overview` | Implemented |
| `/api/monitoring/events` | Implemented |
| `/dashboard` | Implemented/tested |
| `/info` | Not implemented |
| batch prediction | Not implemented |
| Docker health check | Not applicable; no Dockerfile |

## 8. Performance Evidence

- IndoBERT warmed inference CPU: mean 50,57 ms over 10 local texts.
- Cold model loading dominates first request; startup warm-up is implemented.
- Capture chunk: 3.000 ms by design.
- End-to-end audio-to-alert p50/p95/p99: not measured.
- Whisper time is logged per request but no aggregated benchmark artifact exists.

## 9. Security Review

| Control | Current | Required improvement |
|---|---|---|
| Device identity | Schnorr challenge-response | Production group/curve and audited library |
| Challenge freshness | TTL + used flag | Race/concurrency/replay test |
| Upload authorization | HMAC signed token + TTL | Secret rotation/secure key store |
| Server result binding | Fiat–Shamir proof over result string | Production parameters |
| Audio confidentiality | HTTP default | TLS/mTLS |
| Audio integrity/binding | Not tied to initial device proof | Hash audio + device + timestamp + counter |
| Credentials | `.env` ignored but firmware hardcoded | Remove/rotate/provision securely |
| DoS | Basic API | Rate limit, quotas, max upload size |
| Stored audio | Local files | RBAC, encryption, retention/deletion |

## 10. Known Code/Configuration Gaps

1. Training uses max length 64, runtime classifier uses 512.
2. `AUDIO_PLACEHOLDER` behavior can create a dummy Emergency and must be test-only.
3. Some Python dependencies are unpinned.
4. No Dockerfile/docker-compose/.dockerignore.
5. SQLite and synchronous processing limit scale/reliability.
6. No CI/CD evidence or test coverage report.

## 11. Production Test Matrix

| Dimension | Suggested values | Metric |
|---|---|---|
| SNR | quiet, 20, 10, 5, 0 dB | WER, keyword recall, system recall |
| Distance | 0,25; 0,5; 1; 2; 3 m | Recall/latency |
| Mask | none, surgical, respirator | Recall per group |
| Phrase | explicit, implicit, negated, drill | FP/FN |
| Attack | replay, forged ID, bad proof, token replay | rejection rate |
| Network | delay, loss, disconnect, reconnect | p95 alert, dropped chunks |
| Load | 1, 10, 50 devices | throughput, CPU/RAM, error rate |
| Duration | 1h, 8h, 24h soak | leak/crash/recovery |

## 12. Deployment Gate

Do not call the system production-ready until Docker/controlled environment, TLS, secret removal, message binding, replay tests, field audio metrics, fallback behavior, and latency/reliability targets are verified.

