# dumb.fun — Autonomous Solana Memecoin Ecosystem Simulator

This repository includes a runnable **MVP simulation engine** for a 2024-style Solana memecoin ecosystem with autonomous agents.

## Implemented

- Multi-role AI-agent simulation loop (traders/founders/influencers/scammers/builders/LPs).
- Token lifecycle primitives:
  - launches,
  - buys/sells,
  - liquidity growth,
  - graduation trigger,
  - rug-pull behavior.
- Deterministic on-chain adapter that emits reproducible tx signatures per action.
- Social dynamics primitives (shill posts and token trend extraction).
- Dashboard metrics:
  - PnL leaderboard,
  - trending tokens,
  - token outcomes (active / graduated / rugged).
- Engine-level state validation to catch invalid balances or liquidity.
- Test suite validating activity generation, tx verifiability, state invariants, and dashboard output behavior.

## Quickstart

```bash
python main.py
python -m pytest -q
```

## Project structure

- `src/dumbfun/models.py` — core entities/state.
- `src/dumbfun/engine.py` — simulation runtime + invariant validation.
- `src/dumbfun/onchain.py` — deterministic devnet-like tx adapter.
- `src/dumbfun/policies.py` — role/behavior policy functions.
- `src/dumbfun/dashboard.py` — analytics/leaderboards.
- `tests/test_simulation.py` — regression tests.

## Next steps

- Replace deterministic adapter with real Solana devnet submission/reconciliation.
- Add wallet provisioning and event indexer.
- Add WebSocket-backed UI for launchpad/social/leaderboards.
- Add replay, regime testing, and strategy experimentation workflows.
