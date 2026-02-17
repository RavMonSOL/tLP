import os

from src.dumbfun.prototype import run_server


if __name__ == "__main__":
    mode = os.environ.get("DUMBFUN_EXECUTION_MODE", "deterministic")
    run_server(execution_mode=mode)
