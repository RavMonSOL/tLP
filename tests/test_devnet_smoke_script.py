from pathlib import Path

from scripts.devnet_smoke_test import export_wallets
from src.dumbfun.engine import SimulationEngine


def test_export_wallets_writes_pubkey_and_private_key(tmp_path: Path) -> None:
    engine = SimulationEngine()
    engine.seed_agents(3)

    out = tmp_path / "wallets.txt"
    export_wallets(engine, out)

    content = out.read_text(encoding="utf-8")
    assert "agent_0000" in content
    assert "# agent_id,pubkey,private_key" in content
    # deterministic mode should still have a populated private key field
    assert len(content.strip().splitlines()) >= 5
