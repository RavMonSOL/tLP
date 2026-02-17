from src.dumbfun.dashboard import pnl_leaderboard, trending_tokens
from src.dumbfun.engine import SimulationEngine


def run_demo() -> None:
    engine = SimulationEngine()
    engine.seed_agents(150)
    state = engine.run(50)

    print(f"ticks={state.tick} agents={len(state.agents)} tokens={len(state.tokens)} txs={len(state.tx_history)} posts={len(state.posts)}")
    print("top pnl:", pnl_leaderboard(state, top_n=5))
    print("trending:", trending_tokens(state, top_n=5))


if __name__ == "__main__":
    run_demo()
