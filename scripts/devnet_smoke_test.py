from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dumbfun.engine import EngineConfig, SimulationEngine


def run_devnet_smoke(
    agents: int,
    ticks: int,
    sleep_s: float,
    rpc_url: str,
    lamports: int,
    commitment: str,
) -> dict:
    engine = SimulationEngine(
        EngineConfig(
            execution_mode="devnet",
            seed=7,
            devnet_rpc_url=rpc_url,
            devnet_airdrop_lamports=lamports,
            devnet_commitment=commitment,
        )
    )
    engine.seed_agents(agents)

    # Force at least one verifiable on-chain tx so smoke-test is stable when random behavior is quiet.
    first = next(iter(engine.state.agents.values()))
    heartbeat_tx = engine.chain.submit(
        "smoke",
        first.agent_id,
        token_mint=None,
        amount=0.0,
        price=0.0,
        tick=0,
        wallet_address=first.wallet.address,
    )
    engine.state.tx_history.append(heartbeat_tx)

    for _ in range(ticks):
        engine.step()
        if sleep_s > 0:
            time.sleep(sleep_s)

    state = engine.state
    finalized = sum(1 for tx in state.tx_history if tx.finalized)
    sample = [
        {
            "signature": tx.signature,
            "kind": tx.kind,
            "agent_id": tx.agent_id,
            "slot": tx.slot,
            "finalized": tx.finalized,
        }
        for tx in state.tx_history[:5]
    ]
    return {
        "rpc_url": rpc_url,
        "lamports": lamports,
        "commitment": commitment,
        "tick": state.tick,
        "agents": len(state.agents),
        "tokens": len(state.tokens),
        "transactions": len(state.tx_history),
        "finalized": finalized,
        "sample": sample,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny devnet smoke test for dumb.fun.")
    parser.add_argument("--agents", type=int, default=3, help="Number of agents (default: 3)")
    parser.add_argument("--ticks", type=int, default=1, help="Number of simulation ticks (default: 1)")
    parser.add_argument("--rpc-url", default="https://api.devnet.solana.com", help="Solana devnet RPC URL")
    parser.add_argument("--lamports", type=int, default=1_000_000_000, help="Airdrop lamports amount")
    parser.add_argument("--commitment", default="confirmed", help="Airdrop commitment (processed/confirmed/finalized)")
    parser.add_argument(
        "--sleep-s",
        type=float,
        default=0.0,
        help="Optional delay between ticks to reduce request burst",
    )
    parser.add_argument(
        "--allow-faucet-rate-limit",
        action="store_true",
        help="Treat known faucet daily-limit errors as a successful diagnostic run",
    )
    args = parser.parse_args()

    try:
        result = run_devnet_smoke(args.agents, args.ticks, args.sleep_s, args.rpc_url, args.lamports, args.commitment)
    except Exception as exc:  # pragma: no cover
        msg = str(exc)
        faucet_limited = "devnet faucet has a limit of 1 SOL per project per day" in msg
        if faucet_limited and args.allow_faucet_rate_limit:
            print(
                json.dumps(
                    {
                        "rpc_url": args.rpc_url,
                        "status": "faucet_rate_limited",
                        "detail": msg,
                        "note": "Read RPC works, faucet quota reached for this project/API key.",
                    },
                    indent=2,
                )
            )
            return
        raise SystemExit(
            f"Devnet smoke test failed: {msg}\n"
            "Tip: public RPC/faucet policies can fail with 429 (rate limit) or 403 (forbidden). "
            "For Helius, ensure your API key has airdrop/faucet access on devnet."
        ) from exc

    print(json.dumps(result, indent=2))

    if result["transactions"] == 0:
        raise SystemExit("No transactions were produced; increase agents/ticks.")

    if result["finalized"] == 0:
        raise SystemExit("Transactions were submitted but none finalized.")


if __name__ == "__main__":
    main()
