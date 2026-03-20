import argparse
import asyncio
import time

import httpx


async def worker(client: httpx.AsyncClient, url: str, count: int):
    latencies = []
    ok = 0
    for _ in range(count):
        start = time.perf_counter()
        r = await client.get(url)
        latencies.append((time.perf_counter() - start) * 1000.0)
        if r.status_code == 200:
            ok += 1
    return ok, latencies


async def run(base_url: str, total_requests: int, concurrency: int):
    per_worker = total_requests // concurrency
    remainder = total_requests % concurrency
    url = f"{base_url.rstrip('/')}/health"

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = []
        for i in range(concurrency):
            n = per_worker + (1 if i < remainder else 0)
            tasks.append(worker(client, url, n))
        results = await asyncio.gather(*tasks)

    ok_total = sum(r[0] for r in results)
    all_latencies = [x for r in results for x in r[1]]
    all_latencies.sort()
    p50 = all_latencies[int(0.50 * (len(all_latencies) - 1))]
    p95 = all_latencies[int(0.95 * (len(all_latencies) - 1))]
    print(
        f"main_app health load test: total={total_requests}, ok={ok_total}, "
        f"p50_ms={p50:.2f}, p95_ms={p95:.2f}"
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:8000")
    p.add_argument("--requests", type=int, default=500)
    p.add_argument("--concurrency", type=int, default=25)
    args = p.parse_args()
    asyncio.run(run(args.base_url, args.requests, args.concurrency))


if __name__ == "__main__":
    main()
