from src.dumbfun.dashboard import pnl_leaderboard, token_outcomes, trending_tokens
from src.dumbfun.engine import EngineConfig, SimulationEngine


def test_simulation_generates_activity() -> None:
    engine = SimulationEngine()
    engine.seed_agents(80)
    state = engine.run(20)

    assert state.tick == 20
    assert len(state.tokens) > 0
    assert len(state.tx_history) > 0


def test_transactions_have_signatures() -> None:
    engine = SimulationEngine()
    engine.seed_agents(40)
    state = engine.run(10)

    assert all(tx.signature for tx in state.tx_history)
    assert len({tx.signature for tx in state.tx_history}) == len(state.tx_history)


def test_dashboard_outputs_are_sorted() -> None:
    engine = SimulationEngine()
    engine.seed_agents(100)
    state = engine.run(15)

    leaderboard = pnl_leaderboard(state, top_n=10)
    assert len(leaderboard) <= 10
    assert leaderboard == sorted(leaderboard, key=lambda x: x[1], reverse=True)

    trending = trending_tokens(state, top_n=5)
    assert len(trending) <= 5


def test_state_validation_and_outcomes() -> None:
    engine = SimulationEngine(EngineConfig(initial_sol=50.0, seed=42))
    engine.seed_agents(60)
    state = engine.run(25)

    engine.validate_state()

    outcomes = token_outcomes(state)
    assert outcomes["total"] == len(state.tokens)
    assert outcomes["active"] + outcomes["rugged"] == outcomes["total"]

    leaderboard = pnl_leaderboard(state, top_n=5, initial_sol=50.0)
    assert len(leaderboard) <= 5
