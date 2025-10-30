"""Performance metrics collector."""

import time
from collections import defaultdict
from typing import Dict, List
from datetime import datetime


class MetricsCollector:
    """Collects and analyzes performance metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.start_times: Dict[str, float] = {}
        self.counters: Dict[str, int] = defaultdict(int)

    def record_action(self, action_name: str, duration_ms: float) -> None:
        """Record an action duration.

        Args:
            action_name: Name of the action
            duration_ms: Duration in milliseconds
        """
        self.metrics[action_name].append(duration_ms)
        self.counters[f"{action_name}_count"] += 1

    def start_timer(self, timer_name: str) -> None:
        """Start a named timer.

        Args:
            timer_name: Name of the timer
        """
        self.start_times[timer_name] = time.perf_counter()

    def stop_timer(self, timer_name: str) -> float:
        """Stop a named timer and record the duration.

        Args:
            timer_name: Name of the timer

        Returns:
            Duration in milliseconds
        """
        if timer_name not in self.start_times:
            raise ValueError(f"Timer '{timer_name}' was not started")

        duration = (time.perf_counter() - self.start_times[timer_name]) * 1000
        self.record_action(timer_name, duration)
        del self.start_times[timer_name]

        return duration

    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a counter.

        Args:
            counter_name: Name of the counter
            value: Value to increment by
        """
        self.counters[counter_name] += value

    def get_statistics(self) -> dict:
        """Get statistics for all recorded metrics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "actions": {},
            "counters": dict(self.counters),
            "timestamp": datetime.now().isoformat()
        }

        for action_name, durations in self.metrics.items():
            if durations:
                stats["actions"][action_name] = {
                    "count": len(durations),
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                    "avg_ms": sum(durations) / len(durations),
                    "total_ms": sum(durations),
                    "latest_ms": durations[-1]
                }

        return stats

    def get_action_stats(self, action_name: str) -> dict:
        """Get statistics for a specific action.

        Args:
            action_name: Name of the action

        Returns:
            Dictionary with statistics
        """
        durations = self.metrics.get(action_name, [])

        if not durations:
            return {
                "action": action_name,
                "count": 0,
                "recorded": False
            }

        return {
            "action": action_name,
            "count": len(durations),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "avg_ms": sum(durations) / len(durations),
            "total_ms": sum(durations),
            "latest_ms": durations[-1],
            "all_durations": durations,
            "recorded": True
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.start_times.clear()
        self.counters.clear()

    def export_to_dict(self) -> dict:
        """Export all raw metrics data.

        Returns:
            Dictionary with all metrics
        """
        return {
            "metrics": dict(self.metrics),
            "counters": dict(self.counters),
            "active_timers": list(self.start_times.keys()),
            "timestamp": datetime.now().isoformat()
        }

    def print_summary(self) -> None:
        """Print a formatted summary of metrics."""
        stats = self.get_statistics()

        print("\n" + "=" * 60)
        print("PERFORMANCE METRICS SUMMARY")
        print("=" * 60)

        if stats["actions"]:
            print("\nActions:")
            print("-" * 60)

            for action_name, action_stats in stats["actions"].items():
                print(f"\n{action_name}:")
                print(f"  Count:   {action_stats['count']}")
                print(f"  Min:     {action_stats['min_ms']:.2f}ms")
                print(f"  Max:     {action_stats['max_ms']:.2f}ms")
                print(f"  Avg:     {action_stats['avg_ms']:.2f}ms")
                print(f"  Latest:  {action_stats['latest_ms']:.2f}ms")

        if stats["counters"]:
            print("\nCounters:")
            print("-" * 60)

            for counter_name, counter_value in stats["counters"].items():
                print(f"  {counter_name}: {counter_value}")

        print("\n" + "=" * 60)
        print(f"Generated at: {stats['timestamp']}")
        print("=" * 60 + "\n")
