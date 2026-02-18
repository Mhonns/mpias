"""
RAM Stress Test - Allocates and actively touches ~1 GB of RAM
Runs until Ctrl+C, saves result as timestamped .txt (max 20 files kept)
"""

import time
import signal
import os
import glob
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
TARGET_GB   = 1          # how many GB to allocate
OUTPUT_DIR  = "stress-results"
MAX_FILES   = 20
# ────────────────────────────────────────────────────────────────────────────

TARGET_BYTES = TARGET_GB * 1024 * 1024 * 1024
CHUNK_SIZE   = 1024 * 1024   # 1 MB per chunk – bytearray keeps it physical
NUM_CHUNKS   = TARGET_BYTES // CHUNK_SIZE

start_time   = time.time()
write_passes = 0
running      = True


def handle_exit(sig, frame):
    global running
    running = False


signal.signal(signal.SIGINT,  handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


def save_result(elapsed, passes, actual_mb):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pattern = os.path.join(OUTPUT_DIR, "ram_stress_*.txt")
    files   = sorted(glob.glob(pattern))
    while len(files) >= MAX_FILES:
        os.remove(files.pop(0))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = os.path.join(OUTPUT_DIR, f"ram_stress_{timestamp}.txt")

    with open(filename, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("RAM Stress Test Result\n")
        f.write("=" * 50 + "\n")
        f.write(f"Timestamp    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target RAM   : {TARGET_GB} GB\n")
        f.write(f"Allocated    : {actual_mb:.1f} MB\n")
        f.write(f"Duration     : {elapsed:.2f} seconds\n")
        f.write(f"Write passes : {passes:,}\n")
        f.write(f"Throughput   : {passes * actual_mb / 1024 / elapsed:.2f} GB/s (avg)\n")
        f.write("=" * 50 + "\n")

    print(f"\n✅  Result saved → {filename}")


# ── Allocate memory ──────────────────────────────────────────────────────────
print(f"🧠  RAM Stress Test  –  allocating {TARGET_GB} GB  (press Ctrl+C to stop)")
print(f"    Results will be saved to: {OUTPUT_DIR}/\n")

print(f"    Allocating {NUM_CHUNKS} chunks × 1 MB …", end=" ", flush=True)
chunks = [bytearray(CHUNK_SIZE) for _ in range(NUM_CHUNKS)]
actual_mb = len(chunks) * CHUNK_SIZE / 1024 / 1024
print(f"done  ({actual_mb:.0f} MB allocated)\n")

# ── Main loop – keep writing to every chunk so the OS can't page it out ──────
try:
    while running:
        for i, chunk in enumerate(chunks):
            if not running:
                break
            # Overwrite each MB with a repeating byte pattern
            chunk[:] = bytes([write_passes & 0xFF]) * CHUNK_SIZE

        write_passes += 1
        elapsed = time.time() - start_time
        throughput = write_passes * actual_mb / 1024 / elapsed
        print(f"    ⏱  {elapsed:8.1f}s  |  passes: {write_passes:,}  |  "
              f"{throughput:.2f} GB/s", end="\r")

finally:
    elapsed = time.time() - start_time
    save_result(elapsed, write_passes, actual_mb)
    print(f"\n    Total time   : {elapsed:.2f}s")
    print(f"    Write passes : {write_passes:,}")
    # Release memory explicitly
    del chunks