"""Bot message handler for monitoring and automation."""

import asyncio
import time
from datetime import datetime
from typing import Optional, Callable, List

from telethon.tl.types import Message

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector
from .button_clicker import ButtonClicker

logger = get_logger(__name__)


class BotHandler:
    """Handles bot message monitoring and automated responses."""

    def __init__(
        self,
        client,
        bot_username: str,
        sms_trigger_text: str,
        target_cities: List[str]
    ):
        """Initialize bot handler.

        Args:
            client: Telegram client instance
            bot_username: Bot username to monitor
            sms_trigger_text: Text that triggers SMS detection
            target_cities: List of target cities for booking
        """
        self.client = client
        self.bot_username = bot_username
        self.sms_trigger_text = sms_trigger_text
        self.target_cities = target_cities
        self.button_clicker = ButtonClicker(client.client, bot_username)
        self.metrics = MetricsCollector()
        self.last_message_id = 0

    async def initialize(self) -> None:
        """Initialize handler and get last message ID."""
        messages = await self.client.get_latest_messages(self.bot_username, limit=1)

        if messages:
            self.last_message_id = messages[0].id
            logger.info(f"Initialized with last message ID: {self.last_message_id}")
        else:
            logger.info("No previous messages found")

    def is_sms_notification(self, message: Message) -> bool:
        """Check if message is an SMS notification.

        Args:
            message: Message to check

        Returns:
            True if it's an SMS notification
        """
        if not message.text:
            return False

        return (
            self.sms_trigger_text.lower() in message.text.lower() and
            "/start" in message.text.lower()
        )

    async def monitor_sms(
        self,
        polling_interval_ms: int = 30,
        timeout_seconds: int = 20
    ) -> Optional[Message]:
        """Monitor for SMS notification with ultra-low latency.

        Args:
            polling_interval_ms: Polling interval in milliseconds
            timeout_seconds: Monitoring timeout in seconds

        Returns:
            SMS message if detected, None otherwise
        """
        logger.info(f"Starting intensive SMS monitoring (polling every {polling_interval_ms}ms)")

        start_time = time.time()
        polling_interval = polling_interval_ms / 1000.0

        while (time.time() - start_time) < timeout_seconds:
            try:
                messages = await self.client.get_latest_messages(
                    self.bot_username,
                    limit=1,
                    min_id=self.last_message_id
                )

                if messages and messages[0].id > self.last_message_id:
                    message = messages[0]
                    self.last_message_id = message.id

                    if self.is_sms_notification(message):
                        detection_time = datetime.now()
                        logger.info(f"✅ SMS detected at {detection_time.strftime('%H:%M:%S.%f')[:-3]}")
                        return message

                await asyncio.sleep(polling_interval)

            except Exception as e:
                logger.error(f"Error during SMS monitoring: {e}")
                await asyncio.sleep(polling_interval)

        logger.warning("SMS monitoring timeout reached")
        return None

    async def execute_booking_sequence(
        self,
        sms_message: Message,
        target_shipment_patterns: List[str]
    ) -> dict:
        """Execute ultra-fast booking sequence.

        Args:
            sms_message: The SMS notification message
            target_shipment_patterns: List of shipment patterns to look for

        Returns:
            Dictionary with timing statistics and result
        """
        total_start = time.perf_counter()
        sms_received_time = time.perf_counter()

        stats = {
            "sms_detected_at": datetime.now().isoformat(),
            "stages": {},
            "success": False,
            "error": None
        }

        try:
            # STAGE 1: Send /start command immediately
            logger.info("STAGE 1: Sending /start command...")
            await self.client.send_message(self.bot_username, "/start")
            start_sent_time = time.perf_counter()

            stage1_ms = (start_sent_time - sms_received_time) * 1000
            stats["stages"]["sms_to_start_ms"] = round(stage1_ms, 2)
            logger.info(f"✅ Stage 1: {stage1_ms:.2f}ms (SMS → /start)")

            # Minimal delay for response
            await asyncio.sleep(0.015)

            # STAGE 2: Get menu with shipments
            logger.info("STAGE 2: Retrieving shipment menu...")
            messages = await self.client.get_latest_messages(self.bot_username, limit=1)

            if not messages:
                raise Exception("No menu message received")

            menu_message = messages[0]
            all_buttons = await self.button_clicker.get_all_buttons(menu_message)

            if not all_buttons:
                raise Exception("No buttons found in menu")

            logger.info(f"Found {len(all_buttons)} buttons in menu")

            # STAGE 3: Select target shipment
            logger.info("STAGE 3: Selecting target shipment...")
            shipment_selected = False
            target_button = None

            for pattern in target_shipment_patterns:
                button_info = await self.button_clicker.find_button_by_pattern(
                    menu_message,
                    [pattern]
                )
                if button_info:
                    target_button = button_info
                    break

            if not target_button:
                # Try first available button as fallback
                if all_buttons:
                    target_button = all_buttons[0]
                    logger.warning(f"Using fallback button: {target_button[0]}")

            if target_button:
                button_text, button_data = target_button
                logger.info(f"Selected shipment: {button_text}")

                shipment_click_start = time.perf_counter()
                await self.button_clicker.ultra_fast_click(
                    menu_message,
                    button_data,
                    "select_shipment"
                )
                stage2_ms = (time.perf_counter() - shipment_click_start) * 1000
                stats["stages"]["start_to_select_ms"] = round(stage2_ms, 2)
                stats["selected_shipment"] = button_text
                logger.info(f"✅ Stage 2: {stage2_ms:.2f}ms (/start → select)")

                shipment_selected = True
            else:
                raise Exception("No suitable shipment button found")

            # Minimal delay
            await asyncio.sleep(0.015)

            # STAGE 4: Get confirmation message and click confirm
            logger.info("STAGE 4: Confirming booking...")
            new_messages = await self.client.get_latest_messages(self.bot_username, limit=1)

            if not new_messages:
                raise Exception("No confirmation message received")

            confirm_message = new_messages[0]
            confirm_click_start = time.perf_counter()

            confirm_time = await self.button_clicker.click_confirm_button(confirm_message)

            if confirm_time is not None:
                stage3_ms = confirm_time
                stats["stages"]["select_to_confirm_ms"] = round(stage3_ms, 2)
                logger.info(f"✅ Stage 3: {stage3_ms:.2f}ms (select → confirm)")
            else:
                raise Exception("Confirm button not found or failed to click")

            # Calculate total time
            total_time = (time.perf_counter() - total_start) * 1000
            stats["total_time_ms"] = round(total_time, 2)
            stats["success"] = True

            # Wait for result
            await asyncio.sleep(0.1)

            # Get final result message
            result_messages = await self.client.get_latest_messages(self.bot_username, limit=1)
            if result_messages:
                stats["result_message"] = result_messages[0].text

            logger.info(f"🏆 BOOKING COMPLETED in {total_time:.2f}ms")
            logger.info(f"   SMS → /start: {stage1_ms:.2f}ms")
            logger.info(f"   /start → select: {stage2_ms:.2f}ms")
            logger.info(f"   select → confirm: {stage3_ms:.2f}ms")

        except Exception as e:
            error_msg = f"Booking sequence failed: {e}"
            logger.error(error_msg)
            stats["error"] = str(e)
            stats["total_time_ms"] = round((time.perf_counter() - total_start) * 1000, 2)

        return stats

    def get_metrics(self) -> dict:
        """Get handler metrics.

        Returns:
            Dictionary with metrics
        """
        return self.metrics.get_statistics()
