from src.dumbfun.onchain import DeterministicOnChainAdapter, SolanaDevnetAdapter


def test_wallet_provisioning_is_deterministic_per_agent() -> None:
    adapter = DeterministicOnChainAdapter()
    w1 = adapter.provision_wallet("agent_0001")
    w2 = adapter.provision_wallet("agent_0001")
    w3 = adapter.provision_wallet("agent_0002")

    assert w1.address == w2.address
    assert w1.address != w3.address


def test_submit_marks_finalized_for_deterministic_mode() -> None:
    adapter = DeterministicOnChainAdapter()
    wallet = adapter.provision_wallet("agent_0001")

    tx = adapter.submit(
        "buy",
        "agent_0001",
        "mint_1",
        amount=123.0,
        price=0.1,
        tick=1,
        wallet_address=wallet.address,
    )

    assert tx.signature
    assert tx.finalized is True


def test_request_airdrop_uses_commitment_object() -> None:
    adapter = SolanaDevnetAdapter(rpc_url="https://example.invalid", airdrop_lamports=1_000_000_000, commitment="confirmed")

    captured = {}

    def fake_rpc(method: str, params: list):
        captured["method"] = method
        captured["params"] = params
        return "sig123"

    adapter._rpc = fake_rpc  # type: ignore[method-assign]

    sig = adapter.request_airdrop("Wallet111111111111111111111111111111111")
    assert sig == "sig123"
    assert captured["method"] == "requestAirdrop"
    assert captured["params"][1] == 1_000_000_000
    assert captured["params"][2] == {"commitment": "confirmed"}
