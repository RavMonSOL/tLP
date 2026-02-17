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
  <title>dumb.fun prototype</title>
  <style>
    body { font-family: sans-serif; margin: 20px; background: #0f172a; color: #e2e8f0; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .card { background: #1e293b; padding: 12px; border-radius: 10px; }
    button { padding: 8px 12px; border-radius: 8px; border: 0; background: #22c55e; cursor: pointer; margin-right: 8px; }
    table { width: 100%; border-collapse: collapse; }
    td, th { padding: 6px; border-bottom: 1px solid #334155; text-align: left; }
  </style>
</head>
<body>
  <h1>dumb.fun — working prototype</h1>
  <p>Local simulation API + dashboard</p>
  <button onclick=\"advance(1)\">Step +1</button>
  <button onclick=\"advance(10)\">Step +10</button>
  <button onclick=\"refresh()\">Refresh</button>
  <button onclick=\"runRegimes()\">Run Regime Suite</button>
  <pre id=\"summary\"></pre>
  <pre id=\"experiments\"></pre>

  <div class=\"grid\">
    <div class=\"card\">
      <h3>Top PnL</h3>
      <table id=\"pnl\"></table>
    </div>
    <div class=\"card\">
      <h3>Trending</h3>
      <table id=\"trend\"></table>
    </div>
  </div>

<script>
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
function render(d) {
  document.getElementById('summary').textContent = JSON.stringify({
    tick: d.tick, agents: d.agents, tokens: d.tokens, transactions: d.transactions,
    finalized_transactions: d.finalized_transactions, posts: d.posts, outcomes: d.outcomes, execution_mode: d.execution_mode
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
