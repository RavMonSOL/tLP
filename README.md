# dumb.fun — Autonomous Solana Memecoin Ecosystem Simulator

This repository includes a runnable prototype for a 2024-style Solana memecoin ecosystem simulation.

## What is working now

- Multi-role AI-agent simulation loop (traders/founders/influencers/scammers/builders/LPs).
- Token lifecycle primitives (launch, buy/sell, liquidity, graduation, rugs).
- **Execution adapters**:
  - deterministic adapter for fast local testing,
  - Solana devnet adapter using real JSON-RPC submission (`requestAirdrop`) and signature reconciliation.
- Wallet provisioning for each agent through adapter-level `provision_wallet`.
- Event indexing/reconciliation via `EventIndexer` for signature finalization checks.
- HTTP prototype server with live state and workflow endpoints.
- Optional WebSocket streaming server for live snapshots.
- Replay/regime/strategy experiment workflows.

## Quickstart

```bash
python main.py
python -m pytest -q
```

Run HTTP prototype server (deterministic mode):

```bash
python run_server.py
# open http://127.0.0.1:8787
```

Run HTTP prototype server in devnet mode:

```bash
DUMBFUN_EXECUTION_MODE=devnet python run_server.py
```

Run WebSocket live stream (requires websockets package):

```bash
pip install websockets
python run_ws_server.py
# connect ws://127.0.0.1:8790
```

## API endpoints

- `GET /api/state`
- `POST /api/step?ticks=N`
- `GET /api/workflows/replay?seed=7&ticks=20`
- `GET /api/workflows/regimes?seed=7&ticks=20`
- `GET /api/workflows/strategies?ticks=20`

## Project structure

- `src/dumbfun/engine.py` — simulation runtime + validation.
- `src/dumbfun/onchain.py` — deterministic and real devnet adapters.
- `src/dumbfun/indexer.py` — event reconciliation for transaction signatures.
- `src/dumbfun/prototype.py` — HTTP API + dashboard.
- `src/dumbfun/streaming.py` — WebSocket snapshot streaming.
- `src/dumbfun/workflows.py` — replay/regime/strategy workflows.
