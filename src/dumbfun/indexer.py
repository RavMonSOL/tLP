from __future__ import annotations

from dataclasses import dataclass

from .models import TxRecord
from .onchain import SolanaDevnetAdapter


@dataclass
class ReconciliationResult:
    signature: str
    finalized: bool
    slot: int


class EventIndexer:
    """Reconciles tx records against Solana devnet signature status."""

    def __init__(self, rpc_url: str = "https://api.devnet.solana.com") -> None:
        self.adapter = SolanaDevnetAdapter(rpc_url=rpc_url)

    def reconcile(self, tx: TxRecord) -> ReconciliationResult:
        finalized, slot = self.adapter.reconcile_signature(tx.signature)
        tx.finalized = finalized
        tx.slot = slot
        return ReconciliationResult(signature=tx.signature, finalized=finalized, slot=slot)

    def reconcile_many(self, history: list[TxRecord]) -> list[ReconciliationResult]:
        return [self.reconcile(tx) for tx in history]
