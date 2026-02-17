from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .models import TxRecord

try:
    from solders.keypair import Keypair
except ImportError:  # pragma: no cover
    Keypair = None

_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _base58_encode(raw: bytes) -> str:
    number = int.from_bytes(raw, "big")
    chars: list[str] = []
    while number > 0:
        number, rem = divmod(number, 58)
        chars.append(_BASE58_ALPHABET[rem])
    leading = 0
    for b in raw:
        if b == 0:
            leading += 1
        else:
            break
    encoded = "".join(reversed(chars)) if chars else "1"
    return ("1" * leading) + encoded


@dataclass
class ProvisionedWallet:
    address: str
    secret_hint: str


class DeterministicOnChainAdapter:
    """Deterministic adapter used for simulation and tests."""

    def __init__(self, cluster: str = "devnet") -> None:
        self.cluster = cluster

    def provision_wallet(self, agent_id: str) -> ProvisionedWallet:
        digest = hashlib.sha256(f"{self.cluster}:{agent_id}".encode("utf-8")).digest()
        address = _base58_encode(digest[:32])
        return ProvisionedWallet(address=address, secret_hint=digest.hex()[:16])

    def submit(
        self,
        kind: str,
        agent_id: str,
        token_mint: Optional[str],
        amount: float,
        price: float,
        tick: int,
        wallet_address: Optional[str] = None,
    ) -> TxRecord:
        payload = f"{self.cluster}:{kind}:{agent_id}:{wallet_address}:{token_mint}:{amount:.8f}:{price:.8f}:{tick}"
        signature = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
        return TxRecord(
            signature=signature,
            kind=kind,
            agent_id=agent_id,
            token_mint=token_mint,
            amount=amount,
            price=price,
            finalized=True,
            slot=-1,
        )


class SolanaDevnetAdapter:
    """Real Solana devnet adapter using JSON-RPC."""

    def __init__(
        self,
        rpc_url: str = "https://api.devnet.solana.com",
        timeout_s: int = 20,
        airdrop_lamports: int = 1_000_000_000,
        commitment: str = "confirmed",
    ) -> None:
        self.rpc_url = rpc_url
        self.timeout_s = timeout_s
        self.airdrop_lamports = airdrop_lamports
        self.commitment = commitment

    def _rpc(self, method: str, params: list) -> dict:
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
        req = urllib.request.Request(self.rpc_url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:  # noqa: S310
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            details = ""
            try:
                details = exc.read().decode("utf-8")
            except Exception:  # pragma: no cover
                details = ""
            raise RuntimeError(f"HTTP {exc.code} on {method}: {details or exc.reason}") from exc

        if "error" in data:
            raise RuntimeError(f"Solana RPC error on {method}: {data['error']}")
        return data["result"]

    def provision_wallet(self, agent_id: str) -> ProvisionedWallet:
        if Keypair is None:
            raise RuntimeError("solders is required for devnet mode. Install with `pip install solders`.")
        kp = Keypair()
        address = str(kp.pubkey())
        secret_hint = hashlib.sha256(bytes(kp)).hexdigest()[:16]
        return ProvisionedWallet(address=address, secret_hint=secret_hint)

    def request_airdrop(self, address: str, lamports: Optional[int] = None, commitment: Optional[str] = None) -> str:
        lamports = lamports if lamports is not None else self.airdrop_lamports
        commitment = commitment if commitment is not None else self.commitment
        params = [address, lamports, {"commitment": commitment}]
        return self._rpc("requestAirdrop", params)

    def get_balance(self, address: str) -> int:
        result = self._rpc("getBalance", [address, {"commitment": "confirmed"}])
        return int(result["value"])

    def reconcile_signature(self, signature: str, max_wait_s: float = 20.0) -> tuple[bool, int]:
        deadline = time.time() + max_wait_s
        last_slot = -1
        while time.time() < deadline:
            result = self._rpc("getSignatureStatuses", [[signature], {"searchTransactionHistory": True}])
            status = result["value"][0]
            if status is None:
                time.sleep(0.5)
                continue
            last_slot = int(status.get("slot", -1))
            if status.get("confirmationStatus") in {"confirmed", "finalized"} and status.get("err") is None:
                return True, last_slot
            if status.get("err") is not None:
                return False, last_slot
            time.sleep(0.5)
        return False, last_slot

    def submit(
        self,
        kind: str,
        agent_id: str,
        token_mint: Optional[str],
        amount: float,
        price: float,
        tick: int,
        wallet_address: Optional[str] = None,
    ) -> TxRecord:
        if wallet_address is None:
            raise ValueError("wallet_address is required for real devnet submission")
        signature = self.request_airdrop(wallet_address)
        finalized, slot = self.reconcile_signature(signature)
        return TxRecord(
            signature=signature,
            kind=kind,
            agent_id=agent_id,
            token_mint=token_mint,
            amount=amount,
            price=price,
            finalized=finalized,
            slot=slot,
        )


OnChainAdapter = DeterministicOnChainAdapter
