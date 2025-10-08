#!/usr/bin/env python3
import argparse, asyncio, time, json, csv
import httpx
import random

cpu_url = "http://localhost:8080/work/cpu"
files_url = "http://localhost:8080/work/files"
compress_url = "http://localhost:8080/work/image-compress"

body_cpu = {"payloadSize": 100000, "iterations": 10}
body_files = {"payloadSize": 5, "fileSize": 10000}
body_compress = {"payloadSize": 5, "iterations": 1}

targets = [
    (cpu_url, body_cpu),
    (files_url, body_files),
    (compress_url, body_compress),
    ]

async def worker(client, stop_evt, out_q, rps_per_worker):
    interval = 1.0 / rps_per_worker
    while not stop_evt.is_set():
        t_start = time.perf_counter()

        url, body = random.choice(targets)
        code = -1
        try:
            r = await client.post(url, json=body, timeout=5.0)
            await r.aread()
            code = r.status_code
        except Exception:
            code = -1

        dt_ms = (time.perf_counter() - t_start) * 1000.0
        if stop_evt.is_set():
            break
        await out_q.put((int(time.time()), dt_ms, code))

        # NEW: sleep to enforce target RPS
        elapsed = time.perf_counter() - t_start
        sleep_time = max(0, interval - elapsed)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)


async def main():


    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--warmupSec", type=int, default=10)
    ap.add_argument("--runSec", type=int, default=120)
    ap.add_argument("--out", default="load_timeseries.csv")
    ap.add_argument("--timeout", type=float, default=5.0)
    ap.add_argument("--targetRPS", type=int, default=50)
    args = ap.parse_args()

    out_q = asyncio.Queue()
    stop_evt = asyncio.Event()

    rps_per_worker = args.targetRPS / args.concurrency

    async with httpx.AsyncClient(http2=False) as client:
        # start workers
        tasks = [asyncio.create_task(worker(client, stop_evt, out_q, rps_per_worker))
         for _ in range(args.concurrency)]

        # warmup (don’t record)
        await asyncio.sleep(args.warmupSec)        

        # record per-second buckets
        if args.warmupSec > 0:
            print("WARMUP DONE")
            with open(args.out, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["ts","rps","avg_ms","p50_ms","p95_ms","ok","err"])
                f.flush()
        with open(args.out, "a", newline="") as f:
            w = csv.writer(f)
            
            # if args.concurrency > 8:
            #     w.writerow(["High intensity"])
            # else:
            #     w.writerow(["Low intensity"])

            current_sec = int(time.time())
            lats = []
            ok = err = 0

            t_end = time.time() + args.runSec
            while time.time() < t_end:
                try:
                    ts, dt_ms, code = await asyncio.wait_for(out_q.get(), timeout=0.2)
                    if ts == current_sec:
                        lats.append(dt_ms)
                        if 200 <= code < 300: ok += 1
                        else: err += 1
                    elif ts > current_sec:
                        # flush old second(s)
                        while current_sec < ts:
                            if lats:
                                lats.sort()
                                n = len(lats)
                                p50 = lats[min(n-1, int(round(0.50*(n-1))))]
                                p95 = lats[min(n-1, int(round(0.95*(n-1))))]
                                avg = sum(lats)/n
                                w.writerow([current_sec, n, f"{avg:.3f}", f"{p50:.3f}", f"{p95:.3f}", ok, err])
                            else:
                                w.writerow([current_sec, 0, "", "", "", 0, 0])
                            f.flush()
                            current_sec += 1
                            lats, ok, err = [], 0, 0
                        # bucket the just-popped sample
                        lats.append(dt_ms)
                        if 200 <= code < 300: ok += 1
                        else: err += 1
                    out_q.task_done()
                except asyncio.TimeoutError:
                    # time ticked with no samples; if the second rolled over, flush empty
                    now_sec = int(time.time())
                    if now_sec > current_sec:
                        w.writerow([current_sec, 0, "", "", "", 0, 0])
                        f.flush()
                        current_sec = now_sec

        stop_evt.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        await out_q.join()
if __name__ == "__main__":
    asyncio.run(main())