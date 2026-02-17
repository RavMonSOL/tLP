# dumb.fun — Autonomous Solana Memecoin Ecosystem Simulator

This repo contains a runnable prototype of a 2024-style Solana memecoin simulation with agent behaviors, API endpoints, and a devnet execution mode.

## Features

- Multi-role AI-agent simulation loop (trader/founder/influencer/scammer/builder/LP).
- Token lifecycle simulation (launch, buy/sell, graduation, rugs).
- Two execution adapters:
  - `deterministic` (local test mode)
  - `devnet` (real Solana JSON-RPC calls + signature reconciliation)
- HTTP dashboard + API (`run_server.py`).
- Optional WebSocket snapshot stream (`run_ws_server.py`).
- Replay/regime/strategy experiment workflows.
- Devnet smoke test script for VS Code (`scripts/devnet_smoke_test.py`).

---

## Dependencies

### Python

- Python **3.10+** (3.11/3.12 recommended)
- `pip`

Install:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` includes:

- `pytest` (testing)
- `websockets` (optional runtime for `run_ws_server.py`)
- `solders` (required for real devnet wallet/public-key generation)

---

## Platform setup

### Windows (VS Code)

1. Install Python from python.org and check **"Add Python to PATH"**.
2. In VS Code, install extensions:
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
3. Open the repo folder in VS Code.
4. Create and activate virtual env in terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run once (Admin PowerShell):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS (optional)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Quick usage

### 1) Run tests

```bash
python -m pytest -q
```

### 2) Run local deterministic simulation demo

```bash
python main.py
```

### 3) Run HTTP server + dashboard

```bash
python run_server.py
# open http://127.0.0.1:8787
```

### 4) Run in devnet execution mode

Linux/macOS:

```bash
DUMBFUN_EXECUTION_MODE=devnet python run_server.py
```

Windows PowerShell:

```powershell
$env:DUMBFUN_EXECUTION_MODE = "devnet"
python run_server.py
```

### 5) Optional WebSocket stream

```bash
python run_ws_server.py
# ws://127.0.0.1:8790
```

---

## Devnet smoke test (for VS Code)

This is the run-on-demand test you asked for.

Script:

```bash
python scripts/devnet_smoke_test.py --agents 1 --ticks 0 --lamports 1000000000 --commitment confirmed --rpc-url "https://devnet.helius-rpc.com/?api-key=<api-key>"
```

What it does:

- boots engine in `devnet` mode,

This matches the documented `requestAirdrop` shape: `params: [address, lamports, {"commitment": "confirmed"}]`.
- seeds wallets,
- runs short simulation,
- prints tx signatures + finalization summary,
- exits non-zero if no txs or no finalized txs.

### Run from VS Code Tasks

Included task file: `.vscode/tasks.json`

Available tasks:

- `dumbfun: tests`
- `dumbfun: run server`
- `dumbfun: devnet smoke (Helius)`
- `dumbfun: rpc rate-limit probe (Helius)`

Open **Terminal → Run Task...** and choose one.

---


### Testing rate limiting with your Helius RPC

If you specifically want to test rate limiting behavior, run:

```bash
python scripts/rpc_rate_limit_probe.py --rpc-url "https://devnet.helius-rpc.com/?api-key=bfcf5be8-dc1e-4ea9-9799-2e8228720b37" --requests 20
```

Interpretation:

- `rate_limited_429 > 0`: you are being rate limited.
- `forbidden_403 > 0`: endpoint/policy denied that method.
- `ok > 0`: RPC is reachable for regular read calls.

Note: some provider endpoints may allow read methods but block faucet-style calls (`requestAirdrop`) with 403.

If your provider has a daily faucet quota (for example: `1 SOL per project per day`), run with:

```bash
python scripts/devnet_smoke_test.py --agents 1 --ticks 0 --lamports 1000000000 --commitment confirmed --rpc-url "https://devnet.helius-rpc.com/?api-key=<api-key>" --allow-faucet-rate-limit
```

That mode treats faucet-quota errors as a successful diagnostic (RPC reachable, faucet exhausted).

## API endpoints

- `GET /api/state`
- `POST /api/step?ticks=N`
- `GET /api/workflows/replay?seed=7&ticks=20`
- `GET /api/workflows/regimes?seed=7&ticks=20`
- `GET /api/workflows/strategies?ticks=20`

---

## Notes

- Current devnet execution bridge maps actions to verifiable devnet signatures using `requestAirdrop` for safety and simplicity.
- This is a prototype execution layer; full signed token trading transactions are a next step.
