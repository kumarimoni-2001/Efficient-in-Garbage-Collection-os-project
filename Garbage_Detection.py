import gc
import tracemalloc
import matplotlib.pyplot as plt
from typing import List, Dict
import sys
import time

class GarbageMonitor:
    def __init__(self):
        self.memory_history = []
        self.leak_counts = []     
        self.time_points = []
        self.step = 0
        self.leaked_objects = []
        
    def _record_state(self, event: str):
        """Record memory usage and garbage state"""
        gc.collect()
        current, peak = tracemalloc.get_traced_memory()
        uncollectable = len(gc.garbage)
        
        self.memory_history.append((current / 1024 / 1024, peak / 1024 / 1024))
        self.leak_counts.append(uncollectable)
        self.time_points.append(f"{self.step}: {event}")
        self.step += 1
        
        if uncollectable > 0:
            self.leaked_objects.extend(gc.garbage)
            print(f"Detected {uncollectable} uncollectable objects at {event}")
    
    def monitor_leaks(self, threshold_mb: float = 0.5):
        """Check for significant memory changes"""
        if len(self.memory_history) > 1:
            current_usage = self.memory_history[-1][0]
            prev_usage = self.memory_history[-2][0]
            if current_usage - prev_usage > threshold_mb:
                print(f"Warning: Memory increased by {current_usage - prev_usage:.2f}MB")
    
    def plot_garbage_stats(self):
        """Generate a bar chart for leak counts with memory usage overlay"""
        fig, ax1 = plt.subplots(figsize=(14, 7))
        
        
        x = range(len(self.time_points))
        ax1.bar(x, self.leak_counts, color='salmon', alpha=0.7, label='Uncollectable Objects')
        ax1.set_xlabel('Events', fontsize=12)
        ax1.set_ylabel('Number of Uncollectable Objects', fontsize=12, color='salmon')
        ax1.tick_params(axis='y', labelcolor='salmon')
        
        
        ax2 = ax1.twinx()
        currents, peaks = zip(*self.memory_history)
        ax2.plot(x, currents, label='Current Memory (MB)', color='blue', marker='o')
        ax2.plot(x, peaks, label='Peak Memory (MB)', color='green', marker='^')
        ax2.set_ylabel('Memory Usage (MB)', fontsize=12, color='blue')
        ax2.tick_params(axis='y', labelcolor='blue')
        
    
        plt.title('Garbage Detection: Uncollectable Objects vs Memory Usage', fontsize=14, pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(self.time_points, rotation=45, ha='right')
        ax1.grid(True, linestyle='--', alpha=0.5)
        
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.tight_layout()
        plt.savefig('garbage_monitor_bar.png', dpi=300)
        plt.show()

def demonstrate_garbage_monitoring():
    tracemalloc.start()
    monitor = GarbageMonitor()
    
    
    monitor._record_state("Initial")
    
    
    print("Creating normal objects...")
    normal_data = [i for i in range(1000000)]
    monitor._record_state("Normal Objects")
    monitor.monitor_leaks()
    
    
    print("\nCreating circular reference...")
    class Node:
        def __init__(self):
            self.next = None
    
    node1 = Node()
    node2 = Node()
    node1.next = node2
    node2.next = node1
    monitor._record_state("Circular Ref")
    monitor.monitor_leaks()
    
    
    print("\nSimulating leaks...")
    leaked_refs = []
    def create_leak():
        data = [i for i in range(500000)]
        leaked_refs.append(data)
    
    for i in range(2):
        create_leak()
        monitor._record_state(f"Leak Sim {i+1}")
        monitor.monitor_leaks()
    
    
    print("\nCleaning up...")
    node1.next = None
    node2.next = None
    leaked_refs.clear()
    del normal_data
    monitor._record_state("Cleanup")
    monitor.monitor_leaks()
    
    monitor.plot_garbage_stats()
    tracemalloc.stop()

if __name__ == "__main__":
    gc.set_debug(gc.DEBUG_LEAK)
    demonstrate_garbage_monitoring()
