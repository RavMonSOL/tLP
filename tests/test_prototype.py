from src.dumbfun.prototype import SimulationService


def test_snapshot_shape() -> None:
    service = SimulationService()
    snap = service.snapshot(top_n=5)

    assert snap["tick"] == 0
    assert snap["agents"] == 150
    assert "outcomes" in snap
    assert len(snap["leaderboard"]) <= 5


def test_step_advances_ticks_and_activity() -> None:
    service = SimulationService()
    before = service.snapshot()
    after = service.step(ticks=5)

    assert after["tick"] == before["tick"] + 5
    assert after["transactions"] >= before["transactions"]


def test_step_validates_input() -> None:
    service = SimulationService()
    try:
        service.step(ticks=0)
    except ValueError as exc:
        assert "ticks must be >= 1" in str(exc)
    else:
        raise AssertionError("expected ValueError")
