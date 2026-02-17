from __future__ import annotations

from collections import Counter

from .models import SimulationState


def pnl_leaderboard(state: SimulationState, top_n: int = 10, initial_sol: float = 20.0) -> list[tuple[str, float]]:
    rows = []
    for agent in state.agents.values():
        mark_value = agent.wallet.sol_balance
        for mint, qty in agent.wallet.token_balances.items():
            token = state.tokens.get(mint)
            if token and not token.rugged:
                mark_value += qty * token.price
        pnl = mark_value - initial_sol
        rows.append((agent.agent_id, pnl))
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[:top_n]


def trending_tokens(state: SimulationState, top_n: int = 5) -> list[tuple[str, int]]:
    ctr = Counter(p.token_mint for p in state.posts if p.token_mint)
    return ctr.most_common(top_n)


def token_outcomes(state: SimulationState) -> dict[str, int]:
    rugged = sum(1 for token in state.tokens.values() if token.rugged)
    graduated = sum(1 for token in state.tokens.values() if token.graduated)
    active = len(state.tokens) - rugged
    return {
        "total": len(state.tokens),
        "active": active,
        "graduated": graduated,
        "rugged": rugged,
    }
