from __future__ import annotations

from dataclasses import dataclass

from .dashboard import pnl_leaderboard, token_outcomes
from .engine import EngineConfig, SimulationEngine


@dataclass
class Regime:
    name: str
    buy_size_range: tuple[float, float]
    graduation_liquidity: float


REGIMES = {
    "bull": Regime(name="bull", buy_size_range=(0.4, 1.5), graduation_liquidity=20.0),
    "chop": Regime(name="chop", buy_size_range=(0.1, 0.8), graduation_liquidity=30.0),
    "crash": Regime(name="crash", buy_size_range=(0.05, 0.3), graduation_liquidity=60.0),
}


def replay(seed: int, ticks: int, agents: int = 120) -> dict:
    engine = SimulationEngine(EngineConfig(seed=seed))
    engine.seed_agents(agents)
    state = engine.run(ticks)
    engine.validate_state()
    return {
        "seed": seed,
        "ticks": ticks,
        "tokens": len(state.tokens),
        "txs": len(state.tx_history),
        "outcomes": token_outcomes(state),
        "leaderboard": pnl_leaderboard(state, top_n=5, initial_sol=engine.config.initial_sol),
    }


def run_regime_suite(seed: int, ticks: int, agents: int = 120) -> list[dict]:
    runs: list[dict] = []
    for regime in REGIMES.values():
        config = EngineConfig(
            seed=seed,
            buy_size_range=regime.buy_size_range,
            graduation_liquidity=regime.graduation_liquidity,
        )
        engine = SimulationEngine(config)
        engine.seed_agents(agents)
        state = engine.run(ticks)
        engine.validate_state()
        runs.append(
            {
                "regime": regime.name,
                "tokens": len(state.tokens),
                "txs": len(state.tx_history),
                "outcomes": token_outcomes(state),
                "top_pnl": pnl_leaderboard(state, top_n=1, initial_sol=engine.config.initial_sol)[0][1],
            }
        )
    return runs


def strategy_experiment(seeds: list[int], ticks: int = 30, agents: int = 120) -> dict:
    baselines = [replay(seed=s, ticks=ticks, agents=agents) for s in seeds]
    avg_tokens = sum(run["tokens"] for run in baselines) / max(1, len(baselines))
    avg_txs = sum(run["txs"] for run in baselines) / max(1, len(baselines))
    return {
        "runs": len(baselines),
        "avg_tokens": avg_tokens,
        "avg_txs": avg_txs,
        "samples": baselines,
    }
