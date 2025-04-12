import gc # type: ignore
import random
import psutil # type: ignore
import time
import csv
from collections import deque
import matplotlib # type: ignore
matplotlib.use('TkAgg')  # Ensures compatibility across systems
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore

# ------------------ Configuration ------------------ #
NUM_ITERATIONS = 30
SLEEP_INTERVAL = 1  # seconds
MEMORY_LOG_FILE = "memory_usage_log.csv"
QUEUE_SIZE = 30

# ------------------ Setup ------------------ #
sns.set(style="whitegrid", palette="coolwarm")
memory_log = deque(maxlen=QUEUE_SIZE)

process = psutil.Process()

def get_memory_usage_mb():
    """Get current process memory usage in megabytes."""
    return process.memory_info().rss / (1024 * 1024)

def allocate_memory(num_objects=10000, list_size=100):
    """Simulate memory load by allocating random data."""
    return [[random.random() for _ in range(list_size)] for _ in range(num_objects)]

def track_memory():
    """Track memory before, during, and after GC."""
    mem_before = get_memory_usage_mb()
    temp_data = allocate_memory()
    mem_after_alloc = get_memory_usage_mb()
    del temp_data
    gc.collect()
    mem_after_gc = get_memory_usage_mb()
    memory_log.append((mem_before, mem_after_alloc, mem_after_gc))
    return mem_before, mem_after_alloc, mem_after_gc

# ------------------ Live Plotting ------------------ #
plt.ion()
fig, ax = plt.subplots(figsize=(10, 6))

print("📊 Tracking real-time memory usage...")

for i in range(NUM_ITERATIONS):
    before, after_alloc, after_gc = track_memory()

    # Extract values for plotting
    iterations = list(range(1, len(memory_log) + 1))
    mem_before_list = [entry[0] for entry in memory_log]
    mem_allocated_list = [entry[1] for entry in memory_log]
    mem_after_gc_list = [entry[2] for entry in memory_log]

    # Plot update
    ax.clear()
    ax.plot(iterations, mem_before_list, label="Before Allocation", marker='o', linestyle='--')
    ax.plot(iterations, mem_allocated_list, label="After Allocation", marker='s', linestyle=':')
    ax.plot(iterations, mem_after_gc_list, label="After GC", marker='^', linestyle='-')

    ax.set_title("📈 Real-Time Memory Usage with Garbage Collection", fontsize=14, fontweight='bold')
    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Memory (MB)", fontsize=12)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    plt.pause(0.1)
    time.sleep(SLEEP_INTERVAL)

plt.ioff()
plt.show()

# ------------------ Save to CSV ------------------ #
with open(MEMORY_LOG_FILE, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Iteration", "Before Allocation", "After Allocation", "After GC"])
    for idx, (b, a, g) in enumerate(memory_log, start=1):
        writer.writerow([idx, f"{b:.2f}", f"{a:.2f}", f"{g:.2f}"])

print(f"\n✅ Memory usage log saved to: {MEMORY_LOG_FILE}")
 # type: ignore
