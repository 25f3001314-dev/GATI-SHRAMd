"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api.v1.router import api_router
from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Gati Shram API",
    description="Privacy-first predictive mobility intelligence prototype.",
    version=settings.api_version,
)
app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
    allow_origin_regex=r"https://.*(?:-\d+\.app\.github\.dev|\.vercel\.app)",
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_dashboard() -> str:
        """Serve a small API-backed fallback dashboard when only FastAPI is running."""
        return """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gati Shram | Mobility Intelligence</title>
    <style>
        :root { color-scheme: light; font-family: ui-sans-serif, system-ui, sans-serif; background:#f5f6f3; color:#17211f; }
        body { margin:0; min-height:100vh; }
        main { max-width:1040px; margin:0 auto; padding:56px 24px; }
        header { display:flex; justify-content:space-between; gap:24px; align-items:flex-start; border-bottom:1px solid #d9dfda; padding-bottom:28px; }
        h1 { margin:0; font-size:clamp(2rem, 5vw, 3.75rem); letter-spacing:-.04em; line-height:1; }
        p { color:#65726d; line-height:1.6; }
        .eyebrow { color:#16806f; font:700 12px ui-monospace, monospace; letter-spacing:.12em; text-transform:uppercase; }
        .badge { border:1px solid #b8d9d1; color:#136b5d; background:#e7f4f0; padding:8px 10px; font:700 12px ui-monospace, monospace; }
        .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:28px 0; }
        .card { background:#fff; border:1px solid #d9dfda; padding:20px; }
        .label { color:#78847f; font-size:12px; text-transform:uppercase; letter-spacing:.08em; }
        .value { display:block; margin-top:10px; font-size:26px; font-weight:700; }
        .mono { font-family:ui-monospace, monospace; }
        .notice { border-left:3px solid #d98943; background:#fff8ef; padding:16px 18px; }
        a { color:#126e60; font-weight:700; }
        @media (max-width:700px) { header { display:block; } .grid { grid-template-columns:1fr; } .badge { display:inline-block; margin-top:20px; } }
    </style>
</head>
<body>
<main>
    <header><div><div class="eyebrow">Mobility intelligence platform</div><h1>Gati Shram</h1><p>Privacy-first predictive mobility intelligence for governed, aggregated signals.</p></div><div id="mode" class="badge">DEMO DATA</div></header>
    <section class="grid"><div class="card"><span class="label">Data mode</span><strong id="data-mode" class="value mono">Loading</strong></div><div class="card"><span class="label">O-D pairs</span><strong id="pairs" class="value mono">Loading</strong></div><div class="card"><span class="label">Warning corridors</span><strong id="warnings" class="value mono">Loading</strong></div></section>
    <section class="card"><div class="eyebrow">Judge-facing overview</div><h2>Demo environment</h2><p id="summary">Loading API-backed demo signals...</p><div class="notice"><strong>Prototype boundary</strong><p>Signals and model outputs may be synthetic. Historical validation is shown as unavailable until observed mobility data is supplied.</p></div><p><a href="/docs">Open API documentation</a> · <a href="/api/v1/analytics/demo">View demo JSON</a></p></section>
</main>
<script>
Promise.all([fetch('/api/v1/data/status').then(r=>r.json()), fetch('/api/v1/analytics/demo').then(r=>r.json())]).then(([status, demo]) => {
    document.getElementById('mode').textContent = status.data_classification;
    document.getElementById('data-mode').textContent = String(status.data_mode).toUpperCase();
    document.getElementById('pairs').textContent = demo.central_signals ? demo.central_signals.length : 'Not available';
    document.getElementById('warnings').textContent = demo.early_warnings ? demo.early_warnings.filter(x => x.risk_level !== 'LOW').length : 'Not available';
    document.getElementById('summary').textContent = status.fallback_used ? 'Synthetic fallback is active because no public mobility file is configured.' : 'The API is connected. Results are labeled by their configured provenance.';
}).catch(() => { document.getElementById('mode').textContent = 'API UNAVAILABLE'; document.getElementById('summary').textContent = 'The API could not be reached. Start FastAPI and refresh this page.'; });
</script>
</body></html>"""


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return service liveness without contacting external data sources."""
    return {"status": "ok", "environment": settings.environment}
