from __future__ import annotations

import random

from .models import Agent, Role, Token


def should_launch_token(agent: Agent, rng: random.Random) -> bool:
    if Role.FOUNDER not in agent.roles and Role.SCAMMER not in agent.roles:
        return False
    launch_bias = 0.08 + (0.08 if Role.SCAMMER in agent.roles else 0.0)
    return rng.random() < launch_bias


def should_shill(agent: Agent, rng: random.Random) -> bool:
    if Role.INFLUENCER not in agent.roles:
        return False
    return rng.random() < 0.25


def buy_probability(agent: Agent, token: Token) -> float:
    sentiment = max(0.0, min(1.0, agent.greed - agent.fear + 0.5))
    momentum = min(1.0, token.price / 0.01)
    return min(0.95, 0.1 + 0.5 * sentiment + 0.2 * momentum + 0.1 * agent.risk_tolerance)


def should_rug(agent: Agent, token: Token, rng: random.Random) -> bool:
    if Role.SCAMMER not in agent.roles or token.founder_id != agent.agent_id:
        return False
    return token.liquidity > 5 and rng.random() < 0.07
