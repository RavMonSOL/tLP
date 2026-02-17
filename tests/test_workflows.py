from src.dumbfun.workflows import replay, run_regime_suite, strategy_experiment


def test_replay_returns_expected_fields() -> None:
    result = replay(seed=7, ticks=10, agents=50)
    assert result["seed"] == 7
    assert result["ticks"] == 10
    assert result["tokens"] >= 0
    assert "outcomes" in result


def test_regime_suite_runs_all_regimes() -> None:
    results = run_regime_suite(seed=7, ticks=10, agents=50)
    names = {r["regime"] for r in results}
    assert names == {"bull", "chop", "crash"}


def test_strategy_experiment_aggregates_runs() -> None:
    result = strategy_experiment(seeds=[1, 2, 3], ticks=10, agents=50)
    assert result["runs"] == 3
    assert result["avg_tokens"] >= 0
    assert result["avg_txs"] >= 0
