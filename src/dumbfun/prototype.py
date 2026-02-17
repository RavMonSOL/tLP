from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .dashboard import pnl_leaderboard, token_outcomes, trending_tokens
from .engine import EngineConfig, SimulationEngine
from .workflows import replay, run_regime_suite, strategy_experiment


class SimulationService:
    def __init__(self, execution_mode: str = "deterministic") -> None:
        self._lock = threading.Lock()
        self.engine = SimulationEngine(EngineConfig(execution_mode=execution_mode))
        self.engine.seed_agents(150)

    def step(self, ticks: int = 1) -> dict:
        if ticks < 1:
            raise ValueError("ticks must be >= 1")
        with self._lock:
            self.engine.run(ticks)
            self.engine.validate_state()
            return self.snapshot(top_n=10)

    def snapshot(self, top_n: int = 10) -> dict:
        state = self.engine.state
        finalized = sum(1 for tx in state.tx_history if tx.finalized)
        return {
            "tick": state.tick,
            "agents": len(state.agents),
            "tokens": len(state.tokens),
            "transactions": len(state.tx_history),
            "finalized_transactions": finalized,
            "posts": len(state.posts),
            "outcomes": token_outcomes(state),
            "leaderboard": pnl_leaderboard(state, top_n=top_n, initial_sol=self.engine.config.initial_sol),
            "trending": trending_tokens(state, top_n=top_n),
            "execution_mode": self.engine.config.execution_mode,
        }


def _dashboard_html() -> str:
    return """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>dumb.fun prototype</title>
  <style>
    :root {
      --bg: #0b1220;
      --card: #111b2f;
      --muted: #94a3b8;
      --text: #e2e8f0;
      --accent: #22c55e;
      --accent2: #60a5fa;
      --border: #263246;
    }
    body { font-family: Inter, Segoe UI, Roboto, Arial, sans-serif; margin: 20px; background: var(--bg); color: var(--text); }
    h1 { margin: 0 0 6px 0; }
    .muted { color: var(--muted); }
    .toolbar { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0 16px; }
    button { padding: 9px 14px; border-radius: 8px; border: 1px solid var(--border); background: var(--accent); color: #052e16; cursor: pointer; font-weight: 600; }
    button.secondary { background: #0f172a; color: var(--text); }
    .kpis { display: grid; grid-template-columns: repeat(6, minmax(120px, 1fr)); gap: 10px; margin-bottom: 12px; }
    .kpi { background: var(--card); border: 1px solid var(--border); padding: 10px; border-radius: 10px; }
    .kpi .label { font-size: 12px; color: var(--muted); }
    .kpi .val { font-size: 20px; font-weight: 700; margin-top: 2px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .card { background: var(--card); border: 1px solid var(--border); padding: 12px; border-radius: 10px; }
    table { width: 100%; border-collapse: collapse; }
    td, th { padding: 7px; border-bottom: 1px solid var(--border); text-align: left; font-size: 14px; }
    pre { background: #0f172a; border: 1px solid var(--border); padding: 10px; border-radius: 10px; overflow: auto; }
    .progress { height: 10px; background: #0f172a; border: 1px solid var(--border); border-radius: 999px; overflow: hidden; }
    .progress > div { height: 100%; background: linear-gradient(90deg, var(--accent2), var(--accent)); width: 0%; transition: width .3s; }
    @media (max-width: 1100px) { .kpis { grid-template-columns: repeat(3, minmax(120px, 1fr)); } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <h1>dumb.fun — interactive prototype</h1>
  <div class=\"muted\">Launch/trade/social simulation + live metrics dashboard</div>

  <div class=\"toolbar\">
    <button onclick=\"advance(1)\">Step +1</button>
    <button onclick=\"advance(10)\">Step +10</button>
    <button class=\"secondary\" onclick=\"refresh()\">Refresh</button>
    <button class=\"secondary\" onclick=\"runRegimes()\">Run Regime Suite</button>
    <button class=\"secondary\" onclick=\"toggleAuto()\" id=\"autoBtn\">Auto refresh: OFF</button>
  </div>

  <div class=\"kpis\">
    <div class=\"kpi\"><div class=\"label\">Tick</div><div class=\"val\" id=\"k_tick\">0</div></div>
    <div class=\"kpi\"><div class=\"label\">Agents</div><div class=\"val\" id=\"k_agents\">0</div></div>
    <div class=\"kpi\"><div class=\"label\">Tokens</div><div class=\"val\" id=\"k_tokens\">0</div></div>
    <div class=\"kpi\"><div class=\"label\">Transactions</div><div class=\"val\" id=\"k_txs\">0</div></div>
    <div class=\"kpi\"><div class=\"label\">Finalized</div><div class=\"val\" id=\"k_finalized\">0</div></div>
    <div class=\"kpi\"><div class=\"label\">Posts</div><div class=\"val\" id=\"k_posts\">0</div></div>
  </div>

  <div class=\"card\" style=\"margin-bottom: 12px;\">
    <div style=\"display:flex;justify-content:space-between;align-items:center;\">
      <strong>Execution Finalization</strong>
      <span class=\"muted\" id=\"finalizedLabel\">0%</span>
    </div>
    <div class=\"progress\" style=\"margin-top:8px;\"><div id=\"finalizedBar\"></div></div>
  </div>

  <div class=\"grid\">
    <div class=\"card\">
      <h3>Top PnL</h3>
      <table id=\"pnl\"></table>
    </div>
    <div class=\"card\">
      <h3>Trending Tokens</h3>
      <table id=\"trend\"></table>
    </div>
  </div>

  <div class=\"grid\" style=\"margin-top:12px;\">
    <div class=\"card\">
      <h3>State JSON</h3>
      <pre id=\"summary\"></pre>
    </div>
    <div class=\"card\">
      <h3>Experiment Output</h3>
      <pre id=\"experiments\">Run regime suite to populate.</pre>
    </div>
  </div>

<script>
let autoTimer = null;

async function refresh() {
  const r = await fetch('/api/state');
  const d = await r.json();
  render(d);
}

async function advance(ticks) {
  const r = await fetch('/api/step?ticks=' + ticks, {method: 'POST'});
  const d = await r.json();
  render(d);
}

async function runRegimes() {
  const r = await fetch('/api/workflows/regimes?seed=7&ticks=20');
  const d = await r.json();
  document.getElementById('experiments').textContent = JSON.stringify(d, null, 2);
}

function toggleAuto() {
  const btn = document.getElementById('autoBtn');
  if (autoTimer) {
    clearInterval(autoTimer);
    autoTimer = null;
    btn.textContent = 'Auto refresh: OFF';
    return;
  }
  autoTimer = setInterval(refresh, 2500);
  btn.textContent = 'Auto refresh: ON';
}

function render(d) {
  document.getElementById('k_tick').textContent = d.tick;
  document.getElementById('k_agents').textContent = d.agents;
  document.getElementById('k_tokens').textContent = d.tokens;
  document.getElementById('k_txs').textContent = d.transactions;
  document.getElementById('k_finalized').textContent = d.finalized_transactions;
  document.getElementById('k_posts').textContent = d.posts;

  const pct = d.transactions > 0 ? Math.round((d.finalized_transactions / d.transactions) * 100) : 0;
  document.getElementById('finalizedBar').style.width = pct + '%';
  document.getElementById('finalizedLabel').textContent = pct + '% finalized (' + d.execution_mode + ')';

  document.getElementById('summary').textContent = JSON.stringify({
    tick: d.tick,
    outcomes: d.outcomes,
    execution_mode: d.execution_mode,
    finalized_transactions: d.finalized_transactions,
    transactions: d.transactions
  }, null, 2);

  const pnl = [['Agent','PnL']].concat(d.leaderboard || []);
  document.getElementById('pnl').innerHTML = pnl.map((row, i) => `<tr>${row.map(v => i===0 ? `<th>${v}</th>` : `<td>${v}</td>`).join('')}</tr>`).join('');

  const tr = [['Token','Mentions']].concat(d.trending || []);
  document.getElementById('trend').innerHTML = tr.map((row, i) => `<tr>${row.map(v => i===0 ? `<th>${v}</th>` : `<td>${v}</td>`).join('')}</tr>`).join('');
}

refresh();
</script>
</body>
</html>"""


def make_handler(service: SimulationService):
    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, payload: dict | list, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            if parsed.path == "/":
                self._send_html(_dashboard_html())
                return
            if parsed.path == "/api/state":
                top_n = int(qs.get("top_n", ["10"])[0])
                self._send_json(service.snapshot(top_n=top_n))
                return
            if parsed.path == "/api/workflows/replay":
                seed = int(qs.get("seed", ["7"])[0])
                ticks = int(qs.get("ticks", ["20"])[0])
                self._send_json(replay(seed=seed, ticks=ticks))
                return
            if parsed.path == "/api/workflows/regimes":
                seed = int(qs.get("seed", ["7"])[0])
                ticks = int(qs.get("ticks", ["20"])[0])
                self._send_json(run_regime_suite(seed=seed, ticks=ticks))
                return
            if parsed.path == "/api/workflows/strategies":
                ticks = int(qs.get("ticks", ["20"])[0])
                self._send_json(strategy_experiment(seeds=[5, 7, 11], ticks=ticks))
                return
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            if parsed.path == "/api/step":
                ticks = int(qs.get("ticks", ["1"])[0])
                try:
                    payload = service.step(ticks=ticks)
                    self._send_json(payload)
                except ValueError as err:
                    self._send_json({"error": str(err)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    return Handler


def run_server(host: str = "127.0.0.1", port: int = 8787, execution_mode: str = "deterministic") -> None:
    service = SimulationService(execution_mode=execution_mode)
    server = ThreadingHTTPServer((host, port), make_handler(service))
    print(f"dumb.fun prototype server running at http://{host}:{port} mode={execution_mode}")
    server.serve_forever()
