# dumb.fun — Autonomous Solana Memecoin Ecosystem Simulator

This repository now includes a runnable **MVP simulation engine** for a 2024-style Solana memecoin ecosystem with autonomous agents.

## Implemented in this iteration

- Multi-role AI-agent simulation loop (traders/founders/influencers/scammers/builders/LPs).
- Token lifecycle primitives:
  - launches,
  - buys/sells,
  - liquidity growth,
  - graduation trigger,
  - rug-pull behavior.
- Simulated on-chain adapter that emits deterministic tx signatures per action.
- Social dynamics primitives (shill posts and token trend extraction).
- Dashboard helper functions:
  - PnL leaderboard,
  - trending tokens.
- Test suite validating activity generation, tx verifiability, and leaderboard/trend outputs.

## Quickstart

```bash
python main.py
python -m pytest -q
```

## Project structure

- `src/dumbfun/models.py` — core entities/state.
- `src/dumbfun/engine.py` — simulation runtime.
- `src/dumbfun/onchain.py` — deterministic devnet-like tx adapter.
- `src/dumbfun/policies.py` — role/behavior policy functions.
- `src/dumbfun/dashboard.py` — metrics/leaderboards.
- `tests/test_simulation.py` — regression tests.

## Next steps

- Swap deterministic adapter for real Solana devnet submission/reconciliation.
- Add wallet provisioning and event indexer.
- Add WebSocket-backed UI for launchpad/social/leaderboards.
- Add replay, regime testing, and strategy experimentation workflows.
