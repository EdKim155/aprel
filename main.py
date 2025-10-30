#!/usr/bin/env python3
"""Main entry point for automated booking client."""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Optional
import uuid

from auto_booking import (
    BookingClient,
    BotHandler,
    BookingScheduler,
    load_settings,
    SessionManager,
    setup_logging,
    get_logger,
    Notifier
)


logger = get_logger(__name__)


class AutoBookingApp:
    """Main application for automated booking."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the application.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.settings = None
        self.client = None
        self.bot_handler = None
        self.scheduler = None
        self.notifier = None
        self.session_manager = SessionManager()
        self.session_id = str(uuid.uuid4())

    async def initialize(self) -> bool:
        """Initialize all components.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load settings
            logger.info("Loading configuration...")
            self.settings = load_settings(self.config_path)

            # Setup logging
            setup_logging(log_level="INFO")

            # Initialize Telegram client
            logger.info("Initializing Telegram client...")
            session_path = self.session_manager.get_session_path(
                self.settings.telegram.session_name
            )

            self.client = BookingClient(
                api_id=self.settings.telegram.api_id,
                api_hash=self.settings.telegram.api_hash,
                phone=self.settings.telegram.phone,
                session_name=session_path
            )

            if not await self.client.initialize():
                logger.error("Failed to initialize Telegram client")
                return False

            # Initialize bot handler
            target_cities = []
            for target in self.settings.targets:
                target_cities.extend(target.cities)

            self.bot_handler = BotHandler(
                client=self.client,
                bot_username=self.settings.bot.username,
                sms_trigger_text=self.settings.bot.sms_trigger_text,
                target_cities=target_cities
            )

            await self.bot_handler.initialize()

            # Initialize notifier
            self.notifier = Notifier(
                client=self.client,
                notify_user_id=self.settings.notifications.notify_user_id,
                sound_alert=self.settings.notifications.sound_alert
            )

            # Initialize scheduler
            self.scheduler = BookingScheduler()
            self.scheduler.start()

            logger.info("✅ All components initialized successfully")
            return True

        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e}")
            logger.info("Please create config.yaml based on config.example.yaml")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    async def run_immediate_booking(self) -> None:
        """Run immediate booking test (for testing purposes)."""
        logger.info("Starting immediate booking test...")

        self.notifier.print_startup_banner({
            "bot_username": self.settings.bot.username,
            "target_time": "IMMEDIATE TEST",
            "polling_interval_ms": self.settings.performance.polling_interval_ms
        })

        # Start monitoring immediately
        logger.info("Monitoring for SMS notification...")
        logger.info("Please trigger the test mode in the bot (send 🧪 Тест button)")

        sms_message = await self.bot_handler.monitor_sms(
            polling_interval_ms=self.settings.performance.polling_interval_ms,
            timeout_seconds=300  # 5 minutes timeout for testing
        )

        if sms_message:
            logger.info("SMS notification detected! Starting booking sequence...")

            # Get target shipment patterns
            target_patterns = []
            for target in sorted(self.settings.targets, key=lambda x: x.priority):
                target_patterns.extend(target.cities)

            # Execute booking
            stats = await self.bot_handler.execute_booking_sequence(
                sms_message,
                target_patterns
            )

            # Notify user
            await self.notifier.notify_booking_result(stats)

            # Print metrics
            metrics = self.client.get_metrics()
            logger.info(f"Client metrics: {metrics}")

        else:
            logger.warning("No SMS notification detected within timeout period")

    async def run_scheduled_booking(self) -> None:
        """Run booking at scheduled time."""
        target_time_str = self.settings.booking.target_time
        hours, minutes, seconds = map(int, target_time_str.split(':'))

        # Calculate target datetime for today
        now = datetime.now()
        target_datetime = now.replace(
            hour=hours,
            minute=minutes,
            second=seconds,
            microsecond=0
        )

        # If target time has passed today, schedule for tomorrow
        if target_datetime <= now:
            target_datetime += timedelta(days=1)

        self.notifier.print_startup_banner({
            "bot_username": self.settings.bot.username,
            "target_time": target_time_str,
            "polling_interval_ms": self.settings.performance.polling_interval_ms
        })

        logger.info(f"Target booking time: {target_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

        # Wait until preparation time
        preparation_start = target_datetime - timedelta(
            seconds=self.settings.booking.preparation_time_seconds
        )

        logger.info(f"Preparation starts at: {preparation_start.strftime('%Y-%m-%d %H:%M:%S')}")

        # Countdown loop
        while datetime.now() < preparation_start:
            timing = await self.scheduler.calculate_timing(
                target_datetime,
                self.settings.booking.preparation_time_seconds,
                self.settings.booking.monitoring_start_seconds
            )

            seconds_remaining = int(timing["seconds_to_preparation"])
            self.notifier.print_countdown(seconds_remaining, timing["status"])

            await asyncio.sleep(1)

        print()  # New line after countdown
        logger.info("⚡ Preparation phase started!")

        # Send initial /start to prepare the bot
        await self.client.send_message(self.settings.bot.username, "/start")
        logger.info("Preparation /start sent")

        await asyncio.sleep(1)

        # Wait until monitoring start time
        monitoring_start = target_datetime - timedelta(
            seconds=self.settings.booking.monitoring_start_seconds
        )

        while datetime.now() < monitoring_start:
            seconds_remaining = int((monitoring_start - datetime.now()).total_seconds())
            self.notifier.print_countdown(seconds_remaining, "preparation")
            await asyncio.sleep(0.1)

        print()  # New line
        logger.info("🔍 Intensive monitoring started!")

        # Start SMS monitoring
        sms_message = await self.bot_handler.monitor_sms(
            polling_interval_ms=self.settings.performance.polling_interval_ms,
            timeout_seconds=self.settings.booking.monitoring_start_seconds + 10
        )

        if sms_message:
            logger.info("📨 SMS notification detected! Starting booking sequence...")

            # Get target shipment patterns
            target_patterns = []
            for target in sorted(self.settings.targets, key=lambda x: x.priority):
                target_patterns.extend(target.cities)

            # Execute booking
            stats = await self.bot_handler.execute_booking_sequence(
                sms_message,
                target_patterns
            )

            # Notify user
            await self.notifier.notify_booking_result(stats)

        else:
            logger.warning("⚠️ No SMS notification detected within monitoring window")

    async def run(self, mode: str = "immediate") -> None:
        """Run the application.

        Args:
            mode: Run mode ('immediate' or 'scheduled')
        """
        if not await self.initialize():
            logger.error("Initialization failed, exiting...")
            return

        try:
            if mode == "immediate":
                await self.run_immediate_booking()
            elif mode == "scheduled":
                await self.run_scheduled_booking()
            else:
                logger.error(f"Unknown mode: {mode}")

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error during execution: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("Cleaning up...")

        if self.scheduler:
            self.scheduler.stop()

        if self.client:
            await self.client.disconnect()

        logger.info("Cleanup completed")


async def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated Telegram booking client"
    )
    parser.add_argument(
        "--mode",
        choices=["immediate", "scheduled"],
        default="immediate",
        help="Run mode (default: immediate)"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )

    args = parser.parse_args()

    app = AutoBookingApp(config_path=args.config)
    await app.run(mode=args.mode)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
