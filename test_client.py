#!/usr/bin/env python3
"""Test script for automated booking client components."""

import asyncio
import sys
from pathlib import Path

# Add auto_booking to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_booking.utils.logger import setup_logging, get_logger
from auto_booking.utils.metrics import MetricsCollector
from auto_booking.utils.notifier import Notifier
from auto_booking.config.session_manager import SessionManager

logger = get_logger(__name__)


def test_metrics_collector():
    """Test MetricsCollector."""
    print("\n" + "=" * 60)
    print("Testing MetricsCollector")
    print("=" * 60)

    metrics = MetricsCollector()

    # Record some actions
    metrics.record_action("test_action_1", 45.5)
    metrics.record_action("test_action_1", 52.3)
    metrics.record_action("test_action_2", 123.7)

    # Test timer
    metrics.start_timer("timer_test")
    import time
    time.sleep(0.1)
    duration = metrics.stop_timer("timer_test")

    print(f"\n✓ Timer test completed: {duration:.2f}ms")

    # Get statistics
    stats = metrics.get_statistics()
    print(f"\n✓ Statistics collected:")
    print(f"  - Actions recorded: {len(stats['actions'])}")
    print(f"  - test_action_1 avg: {stats['actions']['test_action_1']['avg_ms']:.2f}ms")

    # Print summary
    metrics.print_summary()

    return True


def test_session_manager():
    """Test SessionManager."""
    print("\n" + "=" * 60)
    print("Testing SessionManager")
    print("=" * 60)

    manager = SessionManager(session_dir="test_sessions")

    # Test session path
    path = manager.get_session_path("test_session")
    print(f"\n✓ Session path: {path}")

    # Test listing
    sessions = manager.list_sessions()
    print(f"✓ Found {len(sessions)} existing sessions")

    return True


async def test_notifier():
    """Test Notifier."""
    print("\n" + "=" * 60)
    print("Testing Notifier")
    print("=" * 60)

    notifier = Notifier(
        client=None,
        notify_user_id=None,
        sound_alert=False
    )

    # Test banner
    notifier.print_startup_banner({
        "bot_username": "test_bot",
        "target_time": "11:30:00",
        "polling_interval_ms": 30
    })

    # Test countdown
    print("\n✓ Testing countdown display:")
    for i in range(5, 0, -1):
        notifier.print_countdown(i, "testing")
        await asyncio.sleep(0.5)

    print("\n")

    # Test success notification
    test_stats = {
        "success": True,
        "selected_shipment": "Test_Shipment_1",
        "total_time_ms": 125.5,
        "stages": {
            "sms_to_start_ms": 45.2,
            "start_to_select_ms": 48.1,
            "select_to_confirm_ms": 32.2
        }
    }

    await notifier.notify_booking_result(test_stats)

    # Test failure notification
    test_stats_fail = {
        "success": False,
        "error": "Connection timeout",
        "total_time_ms": 5000
    }

    await notifier.notify_booking_result(test_stats_fail)

    return True


def test_config_loading():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)

    try:
        from auto_booking.config import create_example_config

        # Create example config
        create_example_config("test_config.example.yaml")
        print("\n✓ Example configuration created")

        # Try to load it (will fail because values are placeholders)
        print("✓ Configuration module loaded successfully")

        return True

    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_imports():
    """Test all module imports."""
    print("\n" + "=" * 60)
    print("Testing Module Imports")
    print("=" * 60)

    modules = [
        "auto_booking",
        "auto_booking.core",
        "auto_booking.core.client",
        "auto_booking.core.bot_handler",
        "auto_booking.core.button_clicker",
        "auto_booking.core.scheduler",
        "auto_booking.config",
        "auto_booking.config.settings",
        "auto_booking.config.session_manager",
        "auto_booking.utils",
        "auto_booking.utils.logger",
        "auto_booking.utils.metrics",
        "auto_booking.utils.notifier",
    ]

    all_success = True

    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except Exception as e:
            print(f"✗ {module_name}: {e}")
            all_success = False

    return all_success


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AUTOMATED BOOKING CLIENT - TEST SUITE")
    print("=" * 60)

    # Setup logging
    setup_logging(log_level="INFO", log_file="logs/test_client.log")

    tests = [
        ("Module Imports", test_imports),
        ("Metrics Collector", test_metrics_collector),
        ("Session Manager", test_session_manager),
        ("Notifier", test_notifier),
        ("Configuration", test_config_loading),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            results[test_name] = result
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60 + "\n")

    return all(results.values())


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
