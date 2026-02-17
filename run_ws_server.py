from src.dumbfun.prototype import SimulationService
from src.dumbfun.streaming import run_ws_stream


if __name__ == "__main__":
    service = SimulationService()
    run_ws_stream(service)
