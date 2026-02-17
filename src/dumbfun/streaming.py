from __future__ import annotations

import asyncio
import json
from typing import Any

from .prototype import SimulationService


def run_ws_stream(service: SimulationService, host: str = "127.0.0.1", port: int = 8790, interval_s: float = 1.0) -> None:
    try:
        import websockets
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("websockets package not installed. Install with `pip install websockets`.") from exc

    async def handler(websocket: Any) -> None:
        while True:
            payload = service.snapshot(top_n=10)
            await websocket.send(json.dumps(payload))
            await asyncio.sleep(interval_s)

    async def main() -> None:
        async with websockets.serve(handler, host, port):
            print(f"dumb.fun websocket stream on ws://{host}:{port}")
            await asyncio.Future()

    asyncio.run(main())
