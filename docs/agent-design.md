# Agent Design

## 1) Roles

Primary role archetypes:

- Trader
- Founder
- Influencer/KOL
- Scammer
- Builder
- Liquidity provider

Agents may be single-role or blended-role with weighted behavioral traits.

## 2) Persistent identity and memory

Each agent stores:

- Static profile: handle, role mix, baseline strategy family.
- Dynamic traits: greed, fear, patience, risk tolerance.
- Reputation vectors: credibility, toxicity, alpha score.
- Memory:
  - Trade outcomes (entry/exit/slippage/PnL).
  - Social outcomes (engagement, follower deltas).
  - Counterparty trust map.

## 3) Decision pipeline

For each cycle:

1. Ingest signals:
   - price/volume/liquidity,
   - social trend scores,
   - wallet and drawdown state,
   - recent wins/losses.
2. Generate candidate actions:
   - buy/sell/hold,
   - launch token,
   - post/comment/attack/shill,
   - coordinate or copy-trade.
3. Score actions with utility:
   - expected return,
   - risk-adjusted penalty,
   - reputation impact,
   - strategic alignment to current meta.
4. Select and execute top policy-compliant action.

## 4) Learning loop

- Short-term adaptation: contextual bandits for action weighting.
- Medium-term adaptation: policy tuning by regime cluster.
- Long-term adaptation: role drift and strategy migration based on historical Sharpe-like objectives.

## 5) Emergent behavior templates

Model the possibility of:

- Pump and dump.
- Fake insider narratives.
- Coordinated buys and wallet clustering.
- Market rotations between memes/sectors.
- Copy trading and reflexive trend amplification.

## 6) Capital management

Each agent has:

- Treasury wallet.
- Hot trading wallet.
- Daily risk budget.
- Position sizing policy (`kelly_fraction`-like bounded).
- Bankruptcy and recovery states.

## 7) Reputation and influence

Follower growth depends on:

- Call accuracy.
- Early discovery of runner tokens.
- Viral content and engagement velocity.
- Historical scam flags and rug association penalties.

