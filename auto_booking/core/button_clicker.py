"""Ultra-fast button clicking logic."""

import time
from typing import Optional, List
from telethon.tl.types import Message, KeyboardButtonCallback
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector

logger = get_logger(__name__)


class ButtonClicker:
    """Handles ultra-fast clicking of inline buttons."""

    def __init__(self, client, bot_username: str):
        """Initialize button clicker.

        Args:
            client: Telegram client instance
            bot_username: Target bot username
        """
        self.client = client
        self.bot_username = bot_username
        self.metrics = MetricsCollector()

    async def ultra_fast_click(
        self,
        message: Message,
        button_data: bytes,
        action_name: str = "click"
    ) -> float:
        """Click a button with minimal latency.

        Args:
            message: Message containing the button
            button_data: Button callback data
            action_name: Name for logging

        Returns:
            Reaction time in milliseconds
        """
        start_time = time.perf_counter()

        try:
            bot_entity = await self.client.get_entity(self.bot_username)

            await self.client(
                GetBotCallbackAnswerRequest(
                    peer=bot_entity,
                    msg_id=message.id,
                    data=button_data
                )
            )

            elapsed = (time.perf_counter() - start_time) * 1000
            self.metrics.record_action(action_name, elapsed)

            logger.debug(f"{action_name} completed in {elapsed:.2f}ms")
            return elapsed

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.error(f"Failed to click button: {e} (after {elapsed:.2f}ms)")
            raise

    async def find_button_by_text(
        self,
        message: Message,
        button_text: str
    ) -> Optional[bytes]:
        """Find button callback data by text.

        Args:
            message: Message with inline keyboard
            button_text: Text to search for

        Returns:
            Button callback data or None
        """
        if not message.reply_markup:
            return None

        for row in message.reply_markup.rows:
            for button in row.buttons:
                if hasattr(button, 'text') and button_text in button.text:
                    if hasattr(button, 'data'):
                        return button.data

        return None

    async def find_button_by_pattern(
        self,
        message: Message,
        patterns: List[str]
    ) -> Optional[tuple]:
        """Find button by multiple text patterns.

        Args:
            message: Message with inline keyboard
            patterns: List of text patterns to match

        Returns:
            Tuple of (button_text, button_data) or None
        """
        if not message.reply_markup:
            return None

        for row in message.reply_markup.rows:
            for button in row.buttons:
                if hasattr(button, 'text'):
                    for pattern in patterns:
                        if pattern.lower() in button.text.lower():
                            if hasattr(button, 'data'):
                                return (button.text, button.data)

        return None

    async def get_all_buttons(self, message: Message) -> List[tuple]:
        """Get all buttons from a message.

        Args:
            message: Message with inline keyboard

        Returns:
            List of tuples (button_text, button_data)
        """
        buttons = []

        if not message.reply_markup:
            return buttons

        for row in message.reply_markup.rows:
            for button in row.buttons:
                if hasattr(button, 'text') and hasattr(button, 'data'):
                    buttons.append((button.text, button.data))

        return buttons

    async def click_button_by_text(
        self,
        message: Message,
        button_text: str
    ) -> Optional[float]:
        """Find and click button by text.

        Args:
            message: Message with inline keyboard
            button_text: Button text to find

        Returns:
            Reaction time in ms or None if button not found
        """
        button_data = await self.find_button_by_text(message, button_text)

        if button_data:
            return await self.ultra_fast_click(
                message,
                button_data,
                f"click_{button_text}"
            )

        logger.warning(f"Button '{button_text}' not found")
        return None

    async def click_confirm_button(self, message: Message) -> Optional[float]:
        """Click the confirmation button.

        Args:
            message: Message with inline keyboard

        Returns:
            Reaction time in ms or None if button not found
        """
        confirm_patterns = ["подтвердить", "confirm", "✅"]

        button_info = await self.find_button_by_pattern(message, confirm_patterns)

        if button_info:
            button_text, button_data = button_info
            return await self.ultra_fast_click(
                message,
                button_data,
                "confirm_booking"
            )

        logger.warning("Confirm button not found")
        return None

    def get_metrics(self) -> dict:
        """Get button clicking metrics.

        Returns:
            Dictionary with metrics
        """
        return self.metrics.get_statistics()
