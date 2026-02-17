from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def rpc_call(rpc_url: str, method: str, params: list | None = None) -> tuple[int, dict | None, str | None]:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}).encode("utf-8")
    req = urllib.request.Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body, None
    except urllib.error.HTTPError as exc:
        return exc.code, None, str(exc)


def run_probe(rpc_url: str, requests: int, sleep_s: float) -> dict:
    summary = {"ok": 0, "rate_limited_429": 0, "forbidden_403": 0, "other_http": 0}
    samples: list[dict] = []

    for i in range(requests):
        code, body, err = rpc_call(rpc_url, "getLatestBlockhash")
        if code == 200 and body and "result" in body:
            summary["ok"] += 1
        elif code == 429:
            summary["rate_limited_429"] += 1
        elif code == 403:
            summary["forbidden_403"] += 1
        else:
            summary["other_http"] += 1

        if i < 5:
            samples.append({"index": i, "http_code": code, "error": err})

        if sleep_s > 0:
            time.sleep(sleep_s)

    return {"rpc_url": rpc_url, "requests": requests, "sleep_s": sleep_s, "summary": summary, "samples": samples}


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Solana RPC for rate limiting (429) and basic access.")
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--sleep-s", type=float, default=0.0)
    args = parser.parse_args()

    result = run_probe(args.rpc_url, args.requests, args.sleep_s)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
