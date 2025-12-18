from __future__ import annotations

import argparse
import asyncio
from statistics import mean
from time import perf_counter
from typing import Dict, List, Tuple

import httpx
import numpy as np


PAYLOAD_TEMPLATE: Dict[str, object] = {
    "instances": [
        {
            "Trip_Distance_km": 10.5,
            "Time_of_Day": "Morning",
            "Day_of_Week": "Weekday",
            "Passenger_Count": 2,
            "Traffic_Conditions": "Medium",
            "Weather": "Clear",
            "Base_Fare": 3.0,
            "Per_Km_Rate": 1.2,
            "Per_Minute_Rate": 0.3,
            "Trip_Duration_Minutes": 25.0,
        }
    ]
}


async def _worker(
    client: httpx.AsyncClient,
    url: str,
    payload: Dict[str, object],
    requests_count: int,
    latencies: List[float],
) -> None:
    for _ in range(requests_count):
        start = perf_counter()
        try:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
        except Exception:
            # Ошибки учитываем как запросы с нулевой длительностью
            # (или можно логировать отдельно, если нужно)
            continue
        else:
            elapsed_ms = (perf_counter() - start) * 1000.0
            latencies.append(elapsed_ms)


async def run_benchmark_once(
    url: str, total_requests: int, concurrency: int
) -> Tuple[int, List[float]]:
    """
    Запустить total_requests запросов при заданном concurrency и вернуть список латенсий (мс).
    """
    latencies: List[float] = []

    base = total_requests // concurrency
    remainder = total_requests % concurrency
    per_worker = [base + (1 if i < remainder else 0) for i in range(concurrency)]

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [
            _worker(client, url, PAYLOAD_TEMPLATE, n_req, latencies)
            for n_req in per_worker
            if n_req > 0
        ]
        await asyncio.gather(*tasks)

    return len(latencies), latencies


def summarize_latencies(latencies: List[float]) -> Dict[str, float]:
    if not latencies:
        return {k: float("nan") for k in ["avg", "q25", "q50", "q90", "q95", "q99"]}

    arr = np.array(latencies, dtype=float)
    return {
        "avg": float(mean(arr)),
        "q25": float(np.percentile(arr, 25)),
        "q50": float(np.percentile(arr, 50)),
        "q90": float(np.percentile(arr, 90)),
        "q95": float(np.percentile(arr, 95)),
        "q99": float(np.percentile(arr, 99)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Нагрузочный тест для /predict сервиса модели такси."
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000/predict",
        help="URL эндпоинта /predict",
    )
    parser.add_argument(
        "--total-requests",
        type=int,
        default=500,
        help="Общее количество запросов на конфигурацию",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        nargs="+",
        default=[1, 2, 5, 10, 20, 50],
        help="Список степеней параллелизма (число одновременных соединений)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(
        f"Запуск нагрузочного теста: url={args.url}, "
        f"total_requests={args.total_requests}, "
        f"concurrency_list={args.concurrency}"
    )
    print("N\tavg_ms\tq25_ms\tq50_ms\tq90_ms\tq95_ms\tq99_ms\tok_requests")

    for n in args.concurrency:
        completed, latencies = asyncio.run(
            run_benchmark_once(args.url, args.total_requests, n)
        )
        stats = summarize_latencies(latencies)
        print(
            f"{n}\t"
            f"{stats['avg']:.2f}\t"
            f"{stats['q25']:.2f}\t"
            f"{stats['q50']:.2f}\t"
            f"{stats['q90']:.2f}\t"
            f"{stats['q95']:.2f}\t"
            f"{stats['q99']:.2f}\t"
            f"{completed}"
        )


if __name__ == "__main__":
    main()
