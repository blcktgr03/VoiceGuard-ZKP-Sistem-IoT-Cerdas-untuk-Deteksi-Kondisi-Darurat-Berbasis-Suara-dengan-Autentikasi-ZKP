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
  <title>Monitoring Dashboard</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #08101f;
      --panel: rgba(13, 18, 30, 0.82);
      --line: rgba(148, 163, 184, 0.14);
      --text: #edf2ff;
      --muted: #93a4bd;
      --good: #2dd4bf;
      --warn: #fbbf24;
      --bad: #fb7185;
      --blue: #60a5fa;
      --shadow: 0 18px 50px rgba(0, 0, 0, 0.38);
      --radius: 22px;
    }

    * { box-sizing: border-box; }
    html, body { min-height: 100%; }
    body {
      margin: 0;
      color: var(--text);
      font-family: "Aptos", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(96, 165, 250, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(45, 212, 191, 0.12), transparent 30%),
        linear-gradient(180deg, #050914 0%, #08101f 100%);
    }

    .shell {
      max-width: 1220px;
      margin: 0 auto;
      padding: 22px 16px 32px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      margin-bottom: 18px;
    }

    .title {
      margin: 0;
      font-size: clamp(1.5rem, 3vw, 2.2rem);
      letter-spacing: -0.04em;
    }

    .subtitle {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 0.95rem;
    }

    .refresh {
      appearance: none;
      border: 1px solid rgba(96, 165, 250, 0.22);
      background: linear-gradient(135deg, rgba(96, 165, 250, 0.18), rgba(45, 212, 191, 0.12));
      color: var(--text);
      border-radius: 999px;
      padding: 11px 16px;
      cursor: pointer;
      font: inherit;
      box-shadow: var(--shadow);
    }

    .hero {
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(15, 22, 36, 0.92), rgba(10, 14, 24, 0.96));
      border-radius: 28px;
      padding: 20px;
      box-shadow: var(--shadow);
      margin-bottom: 16px;
    }

    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .chip {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.05);
      color: var(--muted);
      font-size: 0.9rem;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }

    .stat {
      grid-column: span 3;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: var(--radius);
      padding: 18px;
      min-height: 118px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }

    .stat::before {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba(96, 165, 250, 0.08), transparent 55%);
      pointer-events: none;
    }

    .stat-label {
      color: var(--muted);
      font-size: 0.88rem;
      margin-bottom: 14px;
    }

    .stat-value {
      font-size: clamp(1.65rem, 3vw, 2.2rem);
      font-weight: 700;
      letter-spacing: -0.04em;
    }

    .stat-note {
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.88rem;
    }

    .panel {
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 28px;
      padding: 18px;
      box-shadow: var(--shadow);
    }

    .panel-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      margin-bottom: 14px;
    }

    .panel-title {
      margin: 0;
      font-size: 1rem;
    }

    .panel-subtitle {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 0.9rem;
    }

    .feed {
      display: grid;
      gap: 10px;
    }

    .event {
      border: 1px solid rgba(148, 163, 184, 0.12);
      background: rgba(255, 255, 255, 0.03);
      border-radius: 20px;
      padding: 14px 15px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
    }

    .event-top {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      padding: 7px 10px;
      border-radius: 999px;
      font-size: 0.82rem;
      background: rgba(255, 255, 255, 0.06);
      color: var(--text);
    }

    .pill.good { background: rgba(45, 212, 191, 0.14); color: #8af0e1; }
    .pill.warn { background: rgba(251, 191, 36, 0.14); color: #fde68a; }
    .pill.bad { background: rgba(251, 113, 133, 0.14); color: #fda4af; }
    .pill.blue { background: rgba(96, 165, 250, 0.14); color: #bfdbfe; }

    .event h3 {
      margin: 0;
      font-size: 0.98rem;
      font-weight: 600;
    }

    .event p {
      margin: 6px 0 0;
      color: var(--muted);
      line-height: 1.5;
      max-width: 72ch;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }

    .event-meta {
      display: grid;
      align-content: start;
      gap: 8px;
      text-align: right;
      color: var(--muted);
      font-size: 0.9rem;
      min-width: 160px;
    }

    .empty {
      text-align: center;
      color: var(--muted);
      padding: 18px;
      border-radius: 18px;
      border: 1px dashed rgba(148, 163, 184, 0.18);
    }

    .footer {
      margin-top: 14px;
      text-align: center;
      color: var(--muted);
      font-size: 0.88rem;
    }

    @media (max-width: 980px) {
      .stat { grid-column: span 6; }
    }

    @media (max-width: 720px) {
      .shell { padding: 16px 12px 26px; }
      .topbar, .panel-head, .event { grid-template-columns: 1fr; }
      .topbar, .panel-head { flex-direction: column; align-items: flex-start; }
      .stat { grid-column: span 12; }
      .event-meta { text-align: left; min-width: 0; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div>
        <h1 class="title">Monitoring Dashboard</h1>
      </div>
      <button class="refresh" id="refresh-btn" type="button">Refresh</button>
    </header>

    <section class="hero">
      <div class="chips">
        <div class="chip">Status: <strong id="overall-status">-</strong></div>
        <div class="chip">Update: <strong id="last-refresh">-</strong></div>
        <div class="chip">Auto: <strong>5s</strong></div>
      </div>
    </section>

    <section class="grid" id="stats">
      <div class="stat"><div class="stat-label">Device</div><div class="stat-value" data-key="total_devices">-</div><div class="stat-note">terdaftar</div></div>
      <div class="stat"><div class="stat-label">Aktif</div><div class="stat-value" data-key="active_devices">-</div><div class="stat-note">siap pakai</div></div>
      <div class="stat"><div class="stat-label">Emergency</div><div class="stat-value" data-key="emergency_events_24h">-</div><div class="stat-note">24 jam</div></div>
      <div class="stat"><div class="stat-label">Telegram</div><div class="stat-value" data-key="sent_notifications_24h">-</div><div class="stat-note">terkirim</div></div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <h2 class="panel-title">Live Feed</h2>
          <p class="panel-subtitle">Event terbaru.</p>
        </div>
      </div>
      <div class="feed" id="feed">
        <div class="empty">Memuat...</div>
      </div>
    </section>

    <div class="footer">Data ditarik langsung dari backend FastAPI.</div>
  </main>

  <script>
    const overviewUrl = "/api/monitoring/overview";
    const eventsUrl = "/api/monitoring/events?limit=8";
    const feed = document.getElementById("feed");
    const lastRefresh = document.getElementById("last-refresh");
    const overallStatus = document.getElementById("overall-status");
    const refreshButton = document.getElementById("refresh-btn");
    const statNodes = document.querySelectorAll("[data-key]");

    function formatDate(value) {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return "-";
      return new Intl.DateTimeFormat("id-ID", {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(date);
    }

    function labelClass(label) {
      if (label === "Emergency") return "bad";
      if (label === "Normal") return "good";
      return "warn";
    }

    function notificationClass(status) {
      if (status === "sent") return "good";
      if (status === "failed") return "bad";
      if (status === "skipped") return "warn";
      return "blue";
    }

    function renderOverview(data) {
      statNodes.forEach((node) => {
        const key = node.getAttribute("data-key");
        node.textContent = data[key] ?? "-";
      });
      overallStatus.textContent = data.emergency_events_24h > 0 ? "Waspada" : "Normal";
    }

    function renderEvents(items) {
      if (!items.length) {
        feed.innerHTML = '<div class="empty">Belum ada event.</div>';
        return;
      }

      feed.innerHTML = items.map((item) => {
        const confidence = (item.confidence * 100).toFixed(1);
        return `
          <article class="event">
            <div>
              <div class="event-top">
                <span class="pill blue">${item.device_name}</span>
                <span class="pill">${item.device_id}</span>
                ${item.device_location ? `<span class="pill">${item.device_location}</span>` : ""}
                <span class="pill ${labelClass(item.label)}">${item.label}</span>
                <span class="pill ${notificationClass(item.notification_status)}">${item.notification_status || "none"}</span>
              </div>
              <h3>${item.audio_file_name}</h3>
              <p>${item.transcript_text}</p>
            </div>
            <div class="event-meta">
              <div><strong>${confidence}%</strong></div>
              <div>${formatDate(item.created_at)}</div>
            </div>
          </article>
        `;
      }).join("");
    }

    async function refreshDashboard() {
      refreshButton.disabled = true;
      refreshButton.textContent = "Loading...";
      try {
        const [overviewResponse, eventsResponse] = await Promise.all([
          fetch(overviewUrl),
          fetch(eventsUrl),
        ]);

        if (!overviewResponse.ok || !eventsResponse.ok) {
          throw new Error("data gagal dimuat");
        }

        renderOverview(await overviewResponse.json());
        renderEvents(await eventsResponse.json());
        lastRefresh.textContent = formatDate(new Date().toISOString());
      } catch (error) {
        overallStatus.textContent = "Offline";
        feed.innerHTML = `<div class="empty">${error.message}</div>`;
      } finally {
        refreshButton.disabled = false;
        refreshButton.textContent = "Refresh";
      }
    }

    refreshButton.addEventListener("click", refreshDashboard);
    refreshDashboard();
    setInterval(refreshDashboard, 5000);
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
