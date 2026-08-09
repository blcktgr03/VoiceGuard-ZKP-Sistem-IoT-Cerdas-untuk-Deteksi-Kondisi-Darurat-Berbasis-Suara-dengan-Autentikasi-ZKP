from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from backend.api.dependencies import get_monitoring_service
from backend.api.schemas import MonitoringEventRead, MonitoringOverviewRead
from backend.services.monitoring_service import MonitoringService

router = APIRouter()

_DASHBOARD_HTML = """<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Monitoring Dashboard | Pusat Monitoring Keselamatan</title>
  <style>
    /* Token warna berubah otomatis antara kondisi normal, emergency, dan offline. */
    :root {
      color-scheme: light;
      --bg: #f4f7f9;
      --surface: #ffffff;
      --text: #14213d;
      --muted: #64748b;
      --line: #dce5ea;
      --green: #07884a;
      --green-soft: #eaf8f0;
      --red: #e11d2e;
      --red-soft: #fff0f1;
      --blue: #2563eb;
      --shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
      --radius: 8px;
      --state: var(--green);
      --state-soft: var(--green-soft);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
    }

    body.is-emergency { --state: var(--red); --state-soft: var(--red-soft); }
    body.is-offline { --state: #64748b; --state-soft: #eef2f6; }

    .shell { max-width: 1240px; margin: 0 auto; padding: 22px; }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }
    .title { margin: 0; font-size: 1.35rem; font-weight: 750; }
    .top-meta { display: flex; align-items: center; gap: 12px; color: var(--muted); font-size: 0.86rem; }
    .refresh {
      width: 38px;
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 50%;
      background: var(--surface);
      color: var(--blue);
      cursor: pointer;
      font-size: 1.2rem;
    }
    .refresh:disabled { opacity: 0.55; cursor: wait; }

    .dashboard-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.5fr) minmax(300px, 0.8fr);
      gap: 14px;
    }
    .surface {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }

    .status-banner {
      grid-column: 1 / -1;
      min-height: 210px;
      padding: 26px 30px;
      display: flex;
      align-items: center;
      gap: 28px;
      border-color: color-mix(in srgb, var(--state) 24%, var(--line));
      background: linear-gradient(105deg, var(--state-soft), #ffffff 68%);
      overflow: hidden;
      transition: background 350ms ease, border-color 350ms ease;
    }
    .status-symbol {
      flex: 0 0 132px;
      width: 132px;
      height: 150px;
      display: grid;
      place-items: center;
      color: white;
      background: var(--state);
      font-size: 4rem;
      font-weight: 800;
      clip-path: polygon(50% 0, 92% 16%, 86% 72%, 50% 100%, 14% 72%, 8% 16%);
      filter: drop-shadow(0 8px 12px color-mix(in srgb, var(--state) 25%, transparent));
      animation: status-float 3s ease-in-out infinite;
    }
    .status-copy { flex: 1; min-width: 0; }
    .status-copy h2 { margin: 0; color: var(--state); font-size: clamp(1.7rem, 3vw, 2.6rem); transition: color 300ms ease; }
    .status-copy p { margin: 12px 0 0; color: var(--muted); font-size: 1rem; }
    .state-dot {
      display: inline-block;
      width: 9px;
      height: 9px;
      margin-right: 7px;
      border-radius: 50%;
      background: var(--state);
      animation: status-pulse 1.8s ease-out infinite;
    }
    .device-summary { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }
    .device-chip {
      padding: 8px 11px;
      border: 1px solid color-mix(in srgb, var(--state) 18%, var(--line));
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.72);
      color: var(--muted);
      font-size: 0.78rem;
    }
    .device-chip strong { color: var(--text); margin-left: 4px; }
    .section-label { margin: 0 0 16px; font-size: 0.9rem; font-weight: 750; }

    .stats {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .stat { padding: 17px 20px; min-height: 108px; border-right: 1px solid var(--line); }
    .stat:last-child { border-right: 0; }
    .stat-label { color: var(--muted); font-size: 0.8rem; }
    .stat-row { display: flex; align-items: center; justify-content: space-between; margin-top: 9px; }
    .stat-value { font-size: 2rem; font-weight: 800; color: var(--text); }
    .stat-mark {
      width: 36px;
      height: 36px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      background: var(--state-soft);
      color: var(--state);
      font-weight: 800;
    }

    .audio-panel { grid-column: 2; grid-row: 3; padding: 20px; }
    .audio-status { display: flex; gap: 13px; align-items: center; }
    .mic {
      width: 48px;
      height: 48px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      color: var(--state);
      background: var(--state-soft);
      font-size: 1.5rem;
    }
    .audio-title { color: var(--state); font-weight: 750; }
    .audio-line {
      height: 34px;
      margin: 18px 0;
      opacity: 0.6;
      background: repeating-linear-gradient(90deg, transparent 0 5px, var(--state) 5px 7px, transparent 7px 12px);
      mask-image: linear-gradient(transparent 30%, #000 30% 70%, transparent 70%);
      background-position: 0 0;
      animation: audio-flow 1.2s linear infinite;
    }
    .transcript-box { padding: 15px 0; border-top: 1px solid var(--line); }
    .transcript-label { color: var(--muted); font-size: 0.78rem; margin-bottom: 8px; }
    .transcript { margin: 0; min-height: 44px; line-height: 1.5; font-weight: 600; }
    .confidence { margin-top: 10px; color: var(--state); font-size: 0.82rem; font-weight: 750; }
    .response-box {
      margin-top: 14px;
      padding: 14px;
      border-radius: 6px;
      color: var(--state);
      background: var(--state-soft);
      font-size: 0.84rem;
      font-weight: 700;
    }

    .activity { grid-column: 1; grid-row: 3; padding: 20px; min-width: 0; }
    .activity-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 12px; }
    .activity-head h2 { margin: 0; font-size: 0.95rem; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
    th { padding: 10px; text-align: left; color: var(--muted); font-weight: 650; border-bottom: 1px solid var(--line); }
    td { padding: 11px 10px; border-bottom: 1px solid #edf1f4; vertical-align: top; }
    tr:last-child td { border-bottom: 0; }
    .event-message { max-width: 320px; line-height: 1.4; }
    .badge { display: inline-flex; padding: 5px 8px; border-radius: 999px; font-weight: 700; font-size: 0.72rem; }
    .badge.normal { color: var(--green); background: var(--green-soft); }
    .badge.emergency { color: var(--red); background: var(--red-soft); }
    .empty { padding: 22px; text-align: center; color: var(--muted); }

    body.is-emergency .status-banner { animation: emergency-glow 1.25s ease-in-out infinite alternate; }
    body.is-emergency .status-symbol { animation: emergency-pop 0.85s ease-in-out infinite alternate; }

    @keyframes status-float {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-5px); }
    }
    @keyframes status-pulse {
      0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--state) 38%, transparent); }
      70%, 100% { box-shadow: 0 0 0 9px transparent; }
    }
    @keyframes audio-flow { to { background-position: 24px 0; } }
    @keyframes emergency-glow {
      from { box-shadow: var(--shadow); }
      to { box-shadow: 0 8px 30px rgba(225, 29, 46, 0.18); }
    }
    @keyframes emergency-pop {
      from { transform: scale(1); }
      to { transform: scale(1.045); }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
    }

    @media (max-width: 900px) {
      .dashboard-grid { grid-template-columns: 1fr; }
      .stats, .activity, .audio-panel { grid-column: 1; grid-row: auto; }
    }
    @media (max-width: 620px) {
      .shell { padding: 14px; }
      .top-meta span { display: none; }
      .status-banner { min-height: 0; padding: 22px 18px; gap: 18px; }
      .status-symbol { flex-basis: 82px; width: 82px; height: 94px; font-size: 2.6rem; }
      .status-copy h2 { font-size: 1.45rem; }
      .stats { grid-template-columns: 1fr; }
      .stat { border-right: 0; border-bottom: 1px solid var(--line); }
      .stat:last-child { border-bottom: 0; }
    }
  </style>
</head>
<body class="is-normal">
  <main class="shell">
    <!-- Header menampilkan nama sistem, jam WIB, dan kontrol refresh manual. -->
    <header class="topbar">
      <h1 class="title">Pusat Monitoring Keselamatan</h1>
      <div class="top-meta">
        <span id="clock">-</span>
        <button class="refresh" id="refresh-btn" type="button" title="Perbarui data" aria-label="Perbarui data">&#8635;</button>
      </div>
    </header>

    <div class="dashboard-grid">
      <!-- Event paling baru menentukan warna dan pesan status utama. -->
      <section class="surface status-banner" aria-live="polite">
        <div class="status-symbol" id="status-symbol">&#10003;</div>
        <div class="status-copy">
          <h2 id="status-title">Kondisi Normal</h2>
          <p><span class="state-dot"></span><span id="status-description">Tidak terdeteksi suara bahaya</span></p>
          <div class="device-summary">
            <span class="device-chip">Perangkat <strong id="device-name">Menunggu data</strong></span>
            <span class="device-chip">Lokasi <strong id="device-location">Ruang 1</strong></span>
            <span class="device-chip">Status <strong id="connection-status">Menghubungkan</strong></span>
          </div>
        </div>
      </section>

      <!-- Statistik ringkas dihitung backend untuk periode 24 jam. -->
      <section class="surface stats">
        <div class="stat">
          <div class="stat-label">Kejadian 24 Jam</div>
          <div class="stat-row"><strong class="stat-value" data-key="total_events_24h">-</strong><span class="stat-mark">#</span></div>
        </div>
        <div class="stat">
          <div class="stat-label">Emergency 24 Jam</div>
          <div class="stat-row"><strong class="stat-value" data-key="emergency_events_24h">-</strong><span class="stat-mark">!</span></div>
        </div>
        <div class="stat">
          <div class="stat-label">Perangkat Aktif</div>
          <div class="stat-row"><strong class="stat-value" data-key="active_devices">-</strong><span class="stat-mark">&#10003;</span></div>
        </div>
      </section>

      <!-- Panel audio menampilkan transkrip serta confidence terakhir. -->
      <aside class="surface audio-panel">
        <h2 class="section-label">Audio Terbaru</h2>
        <div class="audio-status">
          <div class="mic">&#9835;</div>
          <div>
            <div class="audio-title" id="audio-title">Menunggu suara</div>
            <div class="transcript-label" id="event-time">Belum ada rekaman</div>
          </div>
        </div>
        <div class="audio-line" aria-hidden="true"></div>
        <div class="transcript-box">
          <div class="transcript-label">Teks suara</div>
          <p class="transcript" id="latest-transcript">Belum ada transkrip</p>
          <div class="confidence" id="latest-confidence">Confidence: -</div>
        </div>
        <div class="response-box" id="response-message">Sistem siap memantau suara pekerja.</div>
      </aside>

      <!-- Tabel memudahkan operator membandingkan event terbaru. -->
      <section class="surface activity">
        <div class="activity-head">
          <h2>Aktivitas Terbaru</h2>
          <span class="transcript-label">Diperbarui setiap 1 detik</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Waktu</th><th>Tipe</th><th>Perangkat</th><th>Pesan</th><th>Confidence</th></tr></thead>
            <tbody id="event-table"><tr><td colspan="5" class="empty">Memuat data...</td></tr></tbody>
          </table>
        </div>
      </section>
    </div>
  </main>

  <script>
    // Endpoint monitoring bersifat read-only dan tidak memerlukan token perangkat.
    const overviewUrl = "/api/monitoring/overview";
    const eventsUrl = "/api/monitoring/events?limit=6";
    const refreshButton = document.getElementById("refresh-btn");
    const statNodes = document.querySelectorAll("[data-key]");
    const eventTable = document.getElementById("event-table");
    let refreshInProgress = false;

    function escapeHtml(value) {
      const node = document.createElement("div");
      node.textContent = value == null ? "" : String(value);
      return node.innerHTML;
    }

    function formatDate(value) {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return "-";
      return new Intl.DateTimeFormat("id-ID", {
        day: "2-digit", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit",
        hour12: false,
        timeZone: "Asia/Jakarta",
      }).format(date);
    }

    function setVisualState(label) {
      // Hanya event terbaru yang mengendalikan keadaan visual dashboard.
      const emergency = label === "Emergency";
      document.body.className = emergency ? "is-emergency" : "is-normal";
      document.getElementById("status-symbol").innerHTML = emergency ? "!" : "&#10003;";
      document.getElementById("status-title").textContent = emergency ? "BAHAYA TERDETEKSI" : "Kondisi Normal";
      document.getElementById("status-description").textContent = emergency
        ? "Segera lakukan pemeriksaan lokasi"
        : "Tidak terdeteksi suara bahaya";
      document.getElementById("audio-title").textContent = emergency
        ? "Suara bahaya terdeteksi"
        : "Tidak terdeteksi suara bahaya";
      document.getElementById("response-message").textContent = emergency
        ? "Tindakan darurat diperlukan. Periksa lokasi pekerja."
        : "Sistem aktif dan siap memantau suara pekerja.";
    }

    function renderOverview(data) {
      statNodes.forEach((node) => {
        node.textContent = data[node.dataset.key] ?? "-";
      });
    }

    function renderLatest(item) {
      if (!item) {
        setVisualState("Normal");
        return;
      }
      setVisualState(item.label);
      document.getElementById("device-name").textContent = item.device_name || "Perangkat";
      document.getElementById("device-location").textContent = "Ruang 1";
      document.getElementById("connection-status").textContent = "Terhubung";
      document.getElementById("latest-transcript").textContent = item.transcript_text || "Tidak ada suara terdeteksi";
      document.getElementById("latest-confidence").textContent = `Confidence: ${(item.confidence * 100).toFixed(1)}%`;
      document.getElementById("event-time").textContent = formatDate(item.created_at);
    }

    function renderEvents(items) {
      if (!items.length) {
        eventTable.innerHTML = '<tr><td colspan="5" class="empty">Belum ada aktivitas.</td></tr>';
        renderLatest(null);
        return;
      }
      renderLatest(items[0]);
      eventTable.innerHTML = items.map((item) => {
        const kind = item.label === "Emergency" ? "emergency" : "normal";
        return `<tr>
          <td>${escapeHtml(formatDate(item.created_at))}</td>
          <td><span class="badge ${kind}">${escapeHtml(item.label)}</span></td>
          <td>${escapeHtml(item.device_name)}</td>
          <td class="event-message">${escapeHtml(item.transcript_text)}</td>
          <td><strong>${(item.confidence * 100).toFixed(1)}%</strong></td>
        </tr>`;
      }).join("");
    }

    async function refreshDashboard() {
      // Guard mencegah request polling baru sebelum request sebelumnya selesai.
      if (refreshInProgress) return;
      refreshInProgress = true;
      refreshButton.disabled = true;
      try {
        const [overviewResponse, eventsResponse] = await Promise.all([
          fetch(overviewUrl, { cache: "no-store" }),
          fetch(eventsUrl, { cache: "no-store" }),
        ]);
        if (!overviewResponse.ok || !eventsResponse.ok) throw new Error("Data gagal dimuat");
        renderOverview(await overviewResponse.json());
        renderEvents(await eventsResponse.json());
      } catch (error) {
        document.body.className = "is-offline";
        document.getElementById("status-symbol").textContent = "?";
        document.getElementById("status-title").textContent = "Sistem Offline";
        document.getElementById("status-description").textContent = error.message;
        document.getElementById("connection-status").textContent = "Backend tidak dapat dihubungi";
      } finally {
        refreshInProgress = false;
        refreshButton.disabled = false;
      }
    }

    function updateClock() {
      // Zona waktu ditentukan eksplisit agar jam konsisten sebagai WIB.
      document.getElementById("clock").textContent = new Intl.DateTimeFormat("id-ID", {
        day: "2-digit", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit", second: "2-digit",
        hour12: false,
        timeZone: "Asia/Jakarta",
      }).format(new Date()) + " WIB";
    }

    refreshButton.addEventListener("click", refreshDashboard);
    updateClock();
    refreshDashboard();
    setInterval(updateClock, 1000);
    setInterval(refreshDashboard, 1000);
  </script>
</body>
</html>
"""


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    """Render the monitoring dashboard."""
    return HTMLResponse(_DASHBOARD_HTML)


@router.get("/monitoring/overview", response_model=MonitoringOverviewRead)
def monitoring_overview(
    service: MonitoringService = Depends(get_monitoring_service),
):
    """Return dashboard summary metrics."""
    return service.get_overview()


@router.get("/monitoring/events", response_model=list[MonitoringEventRead])
def monitoring_events(
    limit: int = 12,
    service: MonitoringService = Depends(get_monitoring_service),
):
    """Return the latest monitoring events."""
    return service.list_recent_events(limit=limit)
