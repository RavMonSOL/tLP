from __future__ import annotations

import hashlib
from typing import Optional

from .models import TxRecord


class OnChainAdapter:
    """Deterministic devnet-like adapter used for simulation and testing."""

    def __init__(self, cluster: str = "devnet") -> None:
        self.cluster = cluster

    def submit(
        self,
        kind: str,
        agent_id: str,
        token_mint: Optional[str],
        amount: float,
        price: float,
        tick: int,
    ) -> TxRecord:
        payload = f"{self.cluster}:{kind}:{agent_id}:{token_mint}:{amount:.8f}:{price:.8f}:{tick}"
        signature = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
        return TxRecord(
            signature=signature,
            kind=kind,
            agent_id=agent_id,
            token_mint=token_mint,
            amount=amount,
            price=price,
        )
