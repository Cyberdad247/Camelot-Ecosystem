#!/usr/bin/env python3
"""
Phase H: Live Dashboard
Real-time metrics display with baseline comparison and anomaly status
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "control_plane"))

from phase_h_integration import get_metrics


class LiveDashboard:
    """Real-time metrics display"""

    def __init__(self, refresh_interval: int = 60, hours: int = 1):
        self.refresh_interval = refresh_interval
        self.hours = hours
        self.metrics = get_metrics()

    def display(self):
        """Display metrics once"""
        self._clear_screen()
        self._print_header()
        self._print_metrics()
        self._print_health()
        self._print_alerts()
        self._print_footer()

    def loop(self):
        """Run continuous dashboard (refresh every N seconds)"""
        try:
            while True:
                self.display()
                time.sleep(self.refresh_interval)
        except KeyboardInterrupt:
            print("\n[EXIT] Dashboard stopped")

    def _clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")

    def _print_header(self):
        """Print dashboard header"""
        timestamp = datetime.now().isoformat()
        print("=" * 80)
        print(f"⚙️  PHASE H LIVE DASHBOARD — {timestamp}")
        print("=" * 80)
        print()

    def _print_metrics(self):
        """Print operation metrics"""
        print("📊 OPERATION METRICS (Last 1 hour)")
        print("-" * 80)

        current_metrics = self.metrics.get_current_metrics()

        if not current_metrics:
            print("  [No data collected yet]")
            print()
            return

        # Header
        header = f"{'Operation':<15} {'Count':<8} {'p50':<8} {'p95':<8} {'p99':<8} {'Errors':<10} {'Status':<10}"
        print(header)
        print("-" * 80)

        # Baseline for comparison
        baseline = {
            'read': {'p95': 1.3},
            'write': {'p95': 2.0},
            'route': {'p95': 0.1},
            'compress': {'p95': 1.586},
        }

        # Print each operation type
        for op_type in sorted(current_metrics.keys()):
            stats = current_metrics[op_type]

            if stats.get('status') != 'ok':
                continue

            count = stats.get('count', 0)
            p50 = stats.get('p50', 0)
            p95 = stats.get('p95', 0)
            p99 = stats.get('p99', 0)
            error_count = stats.get('error_count', 0)
            error_rate = stats.get('error_rate', 0)

            # Status indicator
            baseline_p95 = baseline.get(op_type, {}).get('p95', 999)
            if p95 > baseline_p95 * 3:
                status = "🔴 CRIT"
            elif p95 > baseline_p95 * 1.5:
                status = "🟡 WARN"
            else:
                status = "🟢 OK"

            # Format row
            row = f"{op_type:<15} {count:<8} {p50:<8.2f} {p95:<8.2f} {p99:<8.2f} {error_count:<10} {status:<10}"
            print(row)

        print()

    def _print_health(self):
        """Print system health summary"""
        print("💚 SYSTEM HEALTH")
        print("-" * 80)

        health = self.metrics.get_health_status()

        status_icon = {
            'healthy': '✅ HEALTHY',
            'degraded': '⚠️  DEGRADED',
            'unhealthy': '🔴 UNHEALTHY'
        }

        status = health.get('status', 'unknown')
        icon = status_icon.get(status, '❓ UNKNOWN')

        print(f"  Status:   {icon}")
        print(f"  Summary:  {health.get('summary', 'N/A')}")
        print(f"  Anomalies: {health.get('anomaly_count', 0)} total")
        print()

    def _print_alerts(self):
        """Print recent alerts"""
        print("🚨 RECENT ALERTS")
        print("-" * 80)

        health = self.metrics.get_health_status()
        anomalies = health.get('anomalies', [])

        if not anomalies:
            print("  ✅ No anomalies detected")
            print()
            return

        print(f"  {len(anomalies)} anomaly/anomalies detected:\n")

        for i, anomaly in enumerate(anomalies[:5], 1):  # Show first 5
            severity = anomaly.get('severity', 'unknown')
            metric = anomaly.get('metric_name', 'unknown')
            baseline = anomaly.get('baseline_value', 0)
            current = anomaly.get('current_value', 0)
            reason = anomaly.get('reason', 'no details')

            severity_icon = "🔴" if severity == 'critical' else "🟡"

            print(f"  {i}. {severity_icon} {severity.upper()}: {metric}")
            print(f"     Baseline: {baseline:.4f}, Current: {current:.4f}")
            print(f"     Reason: {reason}")
            print()

        if len(anomalies) > 5:
            print(f"  ... and {len(anomalies) - 5} more")
            print()

    def _print_footer(self):
        """Print footer with info"""
        print("-" * 80)
        print(f"⏱️  Refresh: {self.refresh_interval}s | 📦 DB: control_plane/metrics.db | ⚙️ DB: control_plane/anomalies.db")
        print(f"🔄 Next refresh: {datetime.now().isoformat()}")
        print("=" * 80)


def print_once():
    """Print dashboard once and exit"""
    dashboard = LiveDashboard(refresh_interval=0)
    dashboard.display()


def print_continuous(interval: int = 60):
    """Print dashboard continuously"""
    dashboard = LiveDashboard(refresh_interval=interval)
    dashboard.loop()


def print_detailed():
    """Print detailed metrics report"""
    metrics = get_metrics()
    current = metrics.get_current_metrics()

    print("\n📊 DETAILED METRICS REPORT")
    print("=" * 80)

    for op_type in sorted(current.keys()):
        stats = current[op_type]

        print(f"\n{op_type.upper()}:")
        print("-" * 40)

        for key in ['count', 'success_count', 'error_count', 'error_rate',
                    'min_ms', 'avg_ms', 'p50', 'p95', 'p99', 'max_ms']:
            if key in stats:
                value = stats[key]
                if isinstance(value, float):
                    print(f"  {key:<15} {value:.4f}")
                else:
                    print(f"  {key:<15} {value}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Phase H Live Dashboard')
    parser.add_argument('--mode', choices=['once', 'loop', 'detailed'],
                        default='once', help='Display mode')
    parser.add_argument('--interval', type=int, default=60,
                        help='Refresh interval in seconds (for loop mode)')

    args = parser.parse_args()

    if args.mode == 'once':
        print_once()
    elif args.mode == 'detailed':
        print_detailed()
    else:  # loop
        print_continuous(interval=args.interval)
