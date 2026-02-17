from src.dumbfun.onchain import DeterministicOnChainAdapter


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
