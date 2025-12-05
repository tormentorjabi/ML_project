from __future__ import annotations

import argparse
import copy
from itertools import product
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml  # type: ignore[import-untyped]

from src.experiments.run_experiment import execute_experiment


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        result = yaml.safe_load(file)
        if not isinstance(result, dict):
            raise ValueError("YAML config must be a dictionary")
        return result


def expand_grid(grid: Dict[str, Iterable[object]]) -> List[Dict[str, object]]:
    keys = list(grid.keys())
    values = [grid[key] for key in keys]
    combinations = []
    for combo in product(*values):
        combinations.append(dict(zip(keys, combo)))
    return combinations


def main() -> None:
    parser = argparse.ArgumentParser(description="Run grid search experiments")
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Path to YAML config with grid definition",
    )
    args = parser.parse_args()

    base_config = load_config(args.config)
    grid = base_config["model"]["grid"]
    combinations = expand_grid(grid)

    for params in combinations:
        run_config = copy.deepcopy(base_config)
        run_config["model"] = {"params": params}
        execute_experiment(run_config)


if __name__ == "__main__":
    main()
