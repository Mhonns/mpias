"""
CPU Stress Test - Saturates ~1 core to 90-100%
Runs until Ctrl+C, saves result as timestamped .txt (max 20 files kept)
"""

import time
import signal
import math
import os
import glob
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
OUTPUT_DIR = "stress-results"
MAX_FILES   = 20
# ────────────────────────────────────────────────────────────────────────────

start_time   = time.time()
iterations   = 0
running      = True


def handle_exit(sig, frame):
    global running
    running = False


signal.signal(signal.SIGINT,  handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


def burn_cpu():
    """Pure-Python tight loop – keeps one core pegged near 100%."""
    x = 1.0
    for _ in range(50_000):          # chunk size; yields back to main loop
        x = math.sqrt(x * 1.0000001 + 1.23456789)
    return x


def save_result(elapsed, iters):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Remove oldest files if we already have MAX_FILES
    pattern = os.path.join(OUTPUT_DIR, "cpu_stress_*.txt")
    files   = sorted(glob.glob(pattern))
    while len(files) >= MAX_FILES:
        os.remove(files.pop(0))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = os.path.join(OUTPUT_DIR, f"cpu_stress_{timestamp}.txt")

    with open(filename, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("CPU Stress Test Result\n")
        f.write("=" * 50 + "\n")
        f.write(f"Timestamp   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration    : {elapsed:.2f} seconds\n")
        f.write(f"Iterations  : {iters:,}\n")
        f.write(f"Iter/sec    : {iters / elapsed:,.1f}\n")
        f.write("=" * 50 + "\n")

    print(f"\n✅  Result saved → {filename}")


# ── Main loop ────────────────────────────────────────────────────────────────
print("🔥  CPU Stress Test started  (press Ctrl+C to stop)")
print(f"    Results will be saved to: {OUTPUT_DIR}/\n")

try:
    while running:
        burn_cpu()
        iterations += 1

        # Print live stats every ~5 seconds worth of chunks
        if iterations % 100 == 0:
            elapsed = time.time() - start_time
            print(f"    ⏱  {elapsed:8.1f}s  |  iterations: {iterations:,}", end="\r")

finally:
    elapsed = time.time() - start_time
    save_result(elapsed, iterations)
    print(f"\n    Total time : {elapsed:.2f}s")
    print(f"    Iterations : {iterations:,}")