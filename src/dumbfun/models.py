from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class Role(str, Enum):
    TRADER = "trader"
    FOUNDER = "founder"
    INFLUENCER = "influencer"
    SCAMMER = "scammer"
    BUILDER = "builder"
    LP = "liquidity_provider"


@dataclass
class Wallet:
    address: str
    private_key: str | None = None
    sol_balance: float = 0.0
    token_balances: Dict[str, float] = field(default_factory=dict)


@dataclass
class Agent:
    agent_id: str
    handle: str
    roles: List[Role]
    wallet: Wallet
    risk_tolerance: float
    greed: float
    fear: float
    reputation: float = 0.0
    influence: float = 0.0
    pnl: float = 0.0
    memory: List[str] = field(default_factory=list)


@dataclass
class Token:
    mint: str
    name: str
    ticker: str
    founder_id: str
    supply: float
    price: float = 0.0001
    liquidity: float = 0.0
    graduated: bool = False
    rugged: bool = False


@dataclass
class SocialPost:
    post_id: str
    agent_id: str
    token_mint: str | None
    content: str
    likes: int = 0


@dataclass
class TxRecord:
    signature: str
    kind: str
    agent_id: str
    token_mint: str | None
    amount: float
    price: float
    finalized: bool = False
    slot: int = -1


@dataclass
class SimulationState:
    tick: int = 0
    agents: Dict[str, Agent] = field(default_factory=dict)
    tokens: Dict[str, Token] = field(default_factory=dict)
    posts: List[SocialPost] = field(default_factory=list)
    tx_history: List[TxRecord] = field(default_factory=list)
