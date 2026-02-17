# Implementation Roadmap

## Milestone 0 — Foundation (1-2 weeks)

- Bootstrap mono-repo and service boundaries.
- Define shared event schemas.
- Stand up PostgreSQL + Redis + event bus.
- Implement seedable simulation clock.

Deliverable: deterministic local simulation with synthetic market feed.

## Milestone 1 — Agent + Social Core (2-4 weeks)

- Implement agent identity, memory, and policy loop.
- Build social graph service and engagement scoring.
- Add narrative trend extraction and influence leaderboard.

Deliverable: agents produce social dynamics and strategy shifts.

## Milestone 2 — Launchpad + Market Microstructure (3-5 weeks)

- Implement `dumb.fun` launch pipeline.
- Add bonding curve simulation and graduation logic.
- Add basic AMM/liquidity simulation.

Deliverable: complete token lifecycle in simulation-only mode.

## Milestone 3 — Devnet Execution (3-6 weeks)

- Integrate Solana devnet wallet provisioning.
- Implement intent executor + transaction reconciliation.
- Add wallet explorer and verifiable tx links.

Deliverable: real devnet transactions tied to agent actions.

## Milestone 4 — Hybrid Mirror + Hardening (4-8 weeks)

- Enable mirror mode for real launch execution path.
- Add failure handling, circuit breakers, and risk caps.
- Conduct replay tests and stress tests at 1k+ agents.

Deliverable: stable hybrid simulation with robust observability.

## Milestone 5 — Research Platform (ongoing)

- Regime simulations (bull, chop, crash).
- Policy experiments (anti-rug constraints, fee changes, throttles).
- AI-vs-human interaction studies and strategy benchmarking.

Deliverable: reproducible experiments + exportable analytics.

