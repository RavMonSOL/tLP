from __future__ import annotations

import random
from dataclasses import dataclass

from .models import Agent, Role, SimulationState, SocialPost, Token, Wallet
from .onchain import DeterministicOnChainAdapter, SolanaDevnetAdapter
from .policies import buy_probability, should_launch_token, should_rug, should_shill


@dataclass
class EngineConfig:
    seed: int = 7
    initial_sol: float = 20.0
    buy_size_range: tuple[float, float] = (0.1, 1.0)
    graduation_liquidity: float = 30.0
    execution_mode: str = "deterministic"  # deterministic|devnet
    devnet_rpc_url: str = "https://api.devnet.solana.com"


class SimulationEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.rng = random.Random(self.config.seed)
        if self.config.execution_mode == "devnet":
            self.chain = SolanaDevnetAdapter(rpc_url=self.config.devnet_rpc_url)
        else:
            self.chain = DeterministicOnChainAdapter(cluster="devnet")
        self.state = SimulationState()

    def seed_agents(self, n: int) -> None:
        role_pool = [
            Role.TRADER,
            Role.FOUNDER,
            Role.INFLUENCER,
            Role.SCAMMER,
            Role.BUILDER,
            Role.LP,
        ]
        for i in range(n):
            roles = [self.rng.choice(role_pool)]
            if self.rng.random() < 0.3:
                roles.append(self.rng.choice(role_pool))
            agent_id = f"agent_{i:04d}"
            provisioned = self.chain.provision_wallet(agent_id)
            wallet = Wallet(address=provisioned.address, sol_balance=self.config.initial_sol)
            agent = Agent(
                agent_id=agent_id,
                handle=f"anon_{i:04d}",
                roles=list(dict.fromkeys(roles)),
                wallet=wallet,
                risk_tolerance=self.rng.uniform(0.1, 1.0),
                greed=self.rng.uniform(0.0, 1.0),
                fear=self.rng.uniform(0.0, 1.0),
            )
            self.state.agents[agent.agent_id] = agent

    def step(self) -> None:
        self.state.tick += 1

        for agent in self.state.agents.values():
            if should_launch_token(agent, self.rng):
                self._launch_token(agent)

            if self.state.tokens:
                token = self.rng.choice(list(self.state.tokens.values()))
                if not token.rugged:
                    p_buy = buy_probability(agent, token)
                    if self.rng.random() < p_buy:
                        self._buy(agent, token)
                    elif agent.wallet.token_balances.get(token.mint, 0) > 0 and self.rng.random() < 0.2:
                        self._sell(agent, token)

                if should_rug(agent, token, self.rng):
                    self._rug(agent, token)

            if should_shill(agent, self.rng) and self.state.tokens:
                token = self.rng.choice(list(self.state.tokens.values()))
                self._post(agent, token, f"{token.ticker} is the next runner. Not financial advice.")

        self._update_graduation()

    def run(self, ticks: int) -> SimulationState:
        for _ in range(ticks):
            self.step()
        return self.state

    def validate_state(self) -> None:
        for agent in self.state.agents.values():
            if agent.wallet.sol_balance < -1e-9:
                raise ValueError(f"negative SOL balance for {agent.agent_id}")
            for mint, qty in agent.wallet.token_balances.items():
                if qty < -1e-9:
                    raise ValueError(f"negative token balance for {agent.agent_id}:{mint}")

        for token in self.state.tokens.values():
            if token.price <= 0:
                raise ValueError(f"non-positive token price for {token.mint}")
            if token.liquidity < -1e-9:
                raise ValueError(f"negative token liquidity for {token.mint}")

    def _launch_token(self, agent: Agent) -> None:
        mint = f"mint_{self.state.tick}_{len(self.state.tokens):05d}"
        token = Token(
            mint=mint,
            name=f"Meme {len(self.state.tokens)}",
            ticker=f"M{len(self.state.tokens):03d}",
            founder_id=agent.agent_id,
            supply=1_000_000_000,
            price=0.0001,
            liquidity=1.0,
        )
        self.state.tokens[mint] = token
        tx = self.chain.submit(
            "launch",
            agent.agent_id,
            mint,
            amount=0.0,
            price=token.price,
            tick=self.state.tick,
            wallet_address=agent.wallet.address,
        )
        self.state.tx_history.append(tx)
        agent.memory.append(f"launched:{mint}")

    def _buy(self, agent: Agent, token: Token) -> None:
        amount_sol = min(agent.wallet.sol_balance, self.rng.uniform(*self.config.buy_size_range))
        if amount_sol <= 0.01:
            return
        qty = amount_sol / token.price
        agent.wallet.sol_balance -= amount_sol
        agent.wallet.token_balances[token.mint] = agent.wallet.token_balances.get(token.mint, 0.0) + qty
        token.liquidity += amount_sol
        token.price *= 1.01
        tx = self.chain.submit(
            "buy",
            agent.agent_id,
            token.mint,
            amount=qty,
            price=token.price,
            tick=self.state.tick,
            wallet_address=agent.wallet.address,
        )
        self.state.tx_history.append(tx)

    def _sell(self, agent: Agent, token: Token) -> None:
        balance = agent.wallet.token_balances.get(token.mint, 0.0)
        if balance <= 0:
            return
        qty = balance * self.rng.uniform(0.1, 0.7)
        proceeds = qty * token.price
        agent.wallet.token_balances[token.mint] = max(0.0, balance - qty)
        agent.wallet.sol_balance += proceeds
        token.liquidity = max(0.0, token.liquidity - proceeds)
        token.price *= 0.995
        tx = self.chain.submit(
            "sell",
            agent.agent_id,
            token.mint,
            amount=qty,
            price=token.price,
            tick=self.state.tick,
            wallet_address=agent.wallet.address,
        )
        self.state.tx_history.append(tx)

    def _rug(self, agent: Agent, token: Token) -> None:
        stolen = token.liquidity
        token.liquidity = 0.0
        token.rugged = True
        founder = self.state.agents[token.founder_id]
        founder.wallet.sol_balance += stolen
        founder.reputation -= 5
        tx = self.chain.submit(
            "rug",
            agent.agent_id,
            token.mint,
            amount=stolen,
            price=token.price,
            tick=self.state.tick,
            wallet_address=agent.wallet.address,
        )
        self.state.tx_history.append(tx)
        self._post(agent, token, f"Liquidity gone on {token.ticker}. Blame the market.")

    def _post(self, agent: Agent, token: Token, content: str) -> None:
        post = SocialPost(
            post_id=f"post_{self.state.tick}_{len(self.state.posts):06d}",
            agent_id=agent.agent_id,
            token_mint=token.mint,
            content=content,
            likes=int(agent.influence + self.rng.uniform(0, 20)),
        )
        self.state.posts.append(post)
        agent.influence += min(0.5, post.likes / 500)

    def _update_graduation(self) -> None:
        for token in self.state.tokens.values():
            if not token.graduated and not token.rugged and token.liquidity >= self.config.graduation_liquidity:
                token.graduated = True
