# dumb.fun — Autonomous Solana Memecoin Ecosystem Simulator

This repository now includes a runnable **working prototype** for a 2024-style Solana memecoin ecosystem simulation.

## What is working now

- Multi-role AI-agent simulation loop (traders/founders/influencers/scammers/builders/LPs).
- Token lifecycle primitives:
  - launches,
  - buys/sells,
  - liquidity growth,
  - graduation trigger,
  - rug-pull behavior.
- Deterministic on-chain adapter that emits reproducible tx signatures per action.
- Social dynamics primitives (shill posts + trend extraction).
- Invariant checks to detect invalid balances/prices/liquidity.
- **Prototype HTTP server** with:
  - `GET /api/state` for simulation snapshot,
  - `POST /api/step?ticks=N` to advance time,
  - `GET /` basic live dashboard UI.

## Quickstart

```bash
python main.py
python -m pytest -q
```

Run working prototype server:

```bash
python run_server.py
# open http://127.0.0.1:8787
```

## Project structure

- `src/dumbfun/models.py` — core entities/state.
- `src/dumbfun/engine.py` — simulation runtime + invariant validation.
- `src/dumbfun/onchain.py` — deterministic devnet-like tx adapter.
- `src/dumbfun/policies.py` — role/behavior policy functions.
- `src/dumbfun/dashboard.py` — analytics/leaderboards.
- `src/dumbfun/prototype.py` — API service + HTTP dashboard server.
- `run_server.py` — server entrypoint.
- `tests/` — regression tests.

## Next steps

- Replace deterministic adapter with real Solana devnet submission/reconciliation.
- Add wallet provisioning and event indexer.
- Add WebSocket streaming for live updates.
- Add replay, regime testing, and strategy experimentation workflows.
