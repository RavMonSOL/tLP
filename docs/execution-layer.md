# Execution Layer and On-Chain Mirror

## 1) Goal

Convert simulation intents into verifiable Solana transactions while keeping simulation and chain states synchronized in near real time.

## 2) Intent-to-transaction lifecycle

1. Agent creates an `ExecutionIntent`.
2. Gateway validates policy/risk constraints.
3. Planner compiles intent into one or more on-chain instructions.
4. Signer service signs using environment-specific key custody.
5. Broadcaster submits tx and tracks confirmation/finality.
6. Indexer captures outcome and emits `ExecutionResult`.
7. Reconciler applies canonical balances/PnL and updates agent memory.

## 3) Execution intent schema (example)

```json
{
  "intent_id": "uuid",
  "agent_id": "agent_123",
  "intent_type": "BUY_TOKEN",
  "token": "mint_pubkey",
  "size_lamports": 150000000,
  "max_slippage_bps": 350,
  "deadline_unix": 1730000000,
  "idempotency_key": "agent_123:tick_991:buy:mint"
}
```

## 4) Devnet-to-mainnet progression

- Phase 1: local sim + mocked execution.
- Phase 2: devnet real tx execution and reconciliation.
- Phase 3: guarded mainnet mode with strict capital caps and kill switch.

## 5) pump.fun mirror requirement

`dumb.fun` is the mandatory launch interface inside simulation.

Mirror mode responsibilities:

- Translate each internal launch into equivalent real-world launch parameters.
- Keep token metadata synchronized (name, ticker, supply, media hash).
- Capture any drift between expected and actual launch state.

## 6) Reliability controls

- Retry with nonce/priority-fee adaptation.
- Dead-letter queue for failed intents.
- Backoff under RPC degradation.
- Duplicate prevention through idempotency keys.

## 7) Risk and safety controls

- Environment gate (`SIM_ONLY`, `DEVNET_EXEC`, `MAINNET_GUARDED`).
- Strategy-specific max drawdown and position caps.
- Circuit breaker for volatility spikes / repeated failed txs.
- Emergency pause for token launches and liquidity removal.

## 8) Observability

For every action log:

- Agent ID
- Intent ID
- Tx signature(s)
- Compute units and fees
- Fill price and slippage
- PnL impact
- Reconciliation status

