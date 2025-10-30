"""User notification system."""

import sys
from typing import Optional
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)


class Notifier:
    """Handles user notifications about booking results."""

    def __init__(
        self,
        client,
        notify_user_id: Optional[int] = None,
        sound_alert: bool = True
    ):
        """Initialize notifier.

        Args:
            client: Telegram client for sending messages
            notify_user_id: User ID to send notifications to
            sound_alert: Whether to play sound alerts
        """
        self.client = client
        self.notify_user_id = notify_user_id
        self.sound_alert = sound_alert

    async def notify_booking_result(self, stats: dict) -> None:
        """Send notification about booking result.

        Args:
            stats: Booking statistics dictionary
        """
        if stats.get("success"):
            await self._notify_success(stats)
        else:
            await self._notify_failure(stats)

    async def _notify_success(self, stats: dict) -> None:
        """Send success notification.

        Args:
            stats: Booking statistics
        """
        stages = stats.get("stages", {})
        shipment = stats.get("selected_shipment", "Unknown")
        total_time = stats.get("total_time_ms", 0)

        message = (
            "✅ БРОНИРОВАНИЕ УСПЕШНО!\n\n"
            f"📦 Перевозка: {shipment}\n\n"
            "⏱️ Детальные метрики:\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"SMS → /start:     {stages.get('sms_to_start_ms', 0):.0f}ms\n"
            f"/start → выбор:   {stages.get('start_to_select_ms', 0):.0f}ms\n"
            f"Выбор → подтверд: {stages.get('select_to_confirm_ms', 0):.0f}ms\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Общее время:     {total_time:.0f}ms\n"
        )

        if "position_in_queue" in stats:
            message += f"\nПозиция: #{stats['position_in_queue']} в очереди 🏆"

        logger.info(message)
        self._print_colored_box(message, "green")

        if self.sound_alert:
            self._play_sound_alert()

        if self.notify_user_id and self.client:
            try:
                await self.client.client.send_message(
                    self.notify_user_id,
                    message
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {e}")

    async def _notify_failure(self, stats: dict) -> None:
        """Send failure notification.

        Args:
            stats: Booking statistics
        """
        error = stats.get("error", "Unknown error")
        total_time = stats.get("total_time_ms", 0)

        message = (
            "❌ БРОНИРОВАНИЕ НЕ УДАЛОСЬ\n\n"
            f"Причина: {error}\n"
            f"Время выполнения: {total_time:.0f}ms\n"
        )

        logger.error(message)
        self._print_colored_box(message, "red")

        if self.notify_user_id and self.client:
            try:
                await self.client.client.send_message(
                    self.notify_user_id,
                    message
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {e}")

    def notify_status(self, message: str) -> None:
        """Print status notification.

        Args:
            message: Status message
        """
        logger.info(message)
        print(f"\n📊 {message}")

    def print_startup_banner(self, config: dict) -> None:
        """Print startup banner with configuration.

        Args:
            config: Configuration dictionary
        """
        banner = """
╔══════════════════════════════════════════════════════════╗
║        АВТОМАТИЗАЦИЯ БРОНИРОВАНИЯ ПЕРЕВОЗОК             ║
╚══════════════════════════════════════════════════════════╝
"""
        print(banner)

        print(f"📱 Целевой бот: @{config.get('bot_username', 'N/A')}")
        print(f"⏰ Время бронирования: {config.get('target_time', 'N/A')}")
        print(f"⏱️  Интервал проверки: {config.get('polling_interval_ms', 'N/A')}ms")
        print()

    def print_countdown(self, seconds_remaining: int, phase: str) -> None:
        """Print countdown timer.

        Args:
            seconds_remaining: Seconds until target time
            phase: Current phase name
        """
        hours = seconds_remaining // 3600
        minutes = (seconds_remaining % 3600) // 60
        seconds = seconds_remaining % 60

        status_emoji = {
            "waiting": "⏳",
            "preparation": "🔧",
            "monitoring": "👀",
            "completed": "✅"
        }

        emoji = status_emoji.get(phase, "⏱️")

        print(
            f"\r{emoji} До {phase}: {hours:02d}:{minutes:02d}:{seconds:02d}",
            end="",
            flush=True
        )

    def _print_colored_box(self, message: str, color: str) -> None:
        """Print message in a colored box.

        Args:
            message: Message to print
            color: Color name
        """
        # ANSI color codes
        colors = {
            "green": "\033[92m",
            "red": "\033[91m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "reset": "\033[0m"
        }

        color_code = colors.get(color, colors["reset"])
        reset = colors["reset"]

        lines = message.split("\n")
        max_length = max(len(line) for line in lines)

        print(f"\n{color_code}{'=' * (max_length + 4)}{reset}")

        for line in lines:
            padding = max_length - len(line)
            print(f"{color_code}  {line}{' ' * padding}  {reset}")

        print(f"{color_code}{'=' * (max_length + 4)}{reset}\n")

    def _play_sound_alert(self) -> None:
        """Play system sound alert."""
        try:
            # Try to play system beep
            if sys.platform == "win32":
                import winsound
                winsound.Beep(1000, 500)
            else:
                # Linux/Mac - print bell character
                print("\a", flush=True)
        except Exception as e:
            logger.debug(f"Could not play sound alert: {e}")
