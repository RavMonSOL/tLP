from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .dashboard import pnl_leaderboard, token_outcomes, trending_tokens
from .engine import SimulationEngine


class SimulationService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.engine = SimulationEngine()
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
        return {
            "tick": state.tick,
            "agents": len(state.agents),
            "tokens": len(state.tokens),
            "transactions": len(state.tx_history),
            "posts": len(state.posts),
            "outcomes": token_outcomes(state),
            "leaderboard": pnl_leaderboard(state, top_n=top_n, initial_sol=self.engine.config.initial_sol),
            "trending": trending_tokens(state, top_n=top_n),
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
    button { padding: 8px 12px; border-radius: 8px; border: 0; background: #22c55e; cursor: pointer; }
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
  <pre id=\"summary\"></pre>

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
function render(d) {
  document.getElementById('summary').textContent = JSON.stringify({
    tick: d.tick, agents: d.agents, tokens: d.tokens, transactions: d.transactions, posts: d.posts, outcomes: d.outcomes
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
        def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
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
            if parsed.path == "/":
                self._send_html(_dashboard_html())
                return
            if parsed.path == "/api/state":
                qs = parse_qs(parsed.query)
                top_n = int(qs.get("top_n", ["10"])[0])
                self._send_json(service.snapshot(top_n=top_n))
                return
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/step":
                qs = parse_qs(parsed.query)
                ticks = int(qs.get("ticks", ["1"])[0])
                try:
                    payload = service.step(ticks=ticks)
                    self._send_json(payload)
                except ValueError as err:
                    self._send_json({"error": str(err)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    return Handler


def run_server(host: str = "127.0.0.1", port: int = 8787) -> None:
    service = SimulationService()
    server = ThreadingHTTPServer((host, port), make_handler(service))
    print(f"dumb.fun prototype server running at http://{host}:{port}")
    server.serve_forever()
