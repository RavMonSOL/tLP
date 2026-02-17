# dumb.fun — Autonomous Solana Memecoin Ecosystem Simulator

A research-oriented architecture and implementation blueprint for a **2024-style Solana memecoin ecosystem simulation** where autonomous AI agents launch tokens, trade, coordinate socially, and interact with real on-chain state.

## What this repo provides (current state)

This repository currently contains:

- A production-oriented **system architecture** for a hybrid simulation + on-chain execution platform.
- A concrete **agent design** (roles, memory, goals, risk model, learning loop).
- A detailed **execution layer** for converting agent intent into Solana transactions with verification and state reconciliation.
- An implementation **roadmap** from local simulation to devnet mirror mode and eventually mainnet-ready operations.

See:

- `docs/architecture.md`
- `docs/agent-design.md`
- `docs/execution-layer.md`
- `docs/roadmap.md`

## Core principles

1. **Emergence first**: agents act with partial information, bounded rationality, and social influence.
2. **Verifiability always**: all economic actions are traceable with wallet addresses and tx signatures.
3. **Dual-state synchronization**: internal beliefs vs. canonical on-chain state.
4. **Safety rails**: explicit environment gates, treasury controls, and kill switches before real deployment.

## Suggested stack

- **Backend**: TypeScript (Node.js + Fastify/Nest) or Rust services.
- **Chain**: Solana web3.js / Anchor programs.
- **State/Eventing**: PostgreSQL + Redis + Kafka/Redpanda.
- **AI/Multi-agent**: policy models + memory store + orchestrated simulation loop.
- **Frontend**: React + WebSockets for real-time dashboards.

## Intended outcomes

- Research platform for memecoin market dynamics.
- Testbed for strategy stress-testing and AI coordination.
- Hybrid AI-vs-AI and AI-vs-human market experiments.

