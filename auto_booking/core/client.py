"""Telegram client for automated booking."""

import asyncio
from typing import Optional
from datetime import datetime

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import User

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector

logger = get_logger(__name__)


class BookingClient:
    """Telegram client wrapper for booking automation."""

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: str,
        session_name: str = "auto_booking_session"
    ):
        """Initialize the booking client.

        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            phone: Phone number for authentication
            session_name: Session file name
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None
        self.metrics = MetricsCollector()
        self._authorized = False

    async def initialize(self) -> bool:
        """Initialize and authorize the client.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing Telegram client...")
            self.client = TelegramClient(
                self.session_name,
                self.api_id,
                self.api_hash,
                connection_retries=3,
                retry_delay=1,
                auto_reconnect=True,
                sequential_updates=True
            )

            await self.client.connect()

            if not await self.client.is_user_authorized():
                logger.info("Authorization required")
                await self._authorize()
            else:
                logger.info("Already authorized, using existing session")
                self._authorized = True

            me: User = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} (@{me.username})")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            return False

    async def _authorize(self) -> None:
        """Handle user authorization."""
        try:
            await self.client.send_code_request(self.phone)
            logger.info(f"Code sent to {self.phone}")

            code = input("Enter the code you received: ")
            await self.client.sign_in(self.phone, code)

            self._authorized = True
            logger.info("Authorization successful")

        except SessionPasswordNeededError:
            logger.info("2FA enabled, password required")
            password = input("Enter your 2FA password: ")
            await self.client.sign_in(password=password)
            self._authorized = True
            logger.info("2FA authorization successful")

        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            raise

    async def send_message(self, bot_username: str, message: str) -> int:
        """Send a message to a bot.

        Args:
            bot_username: Bot username (with or without @)
            message: Message text

        Returns:
            Message ID of sent message
        """
        start_time = datetime.now()

        if not bot_username.startswith('@'):
            bot_username = f'@{bot_username}'

        result = await self.client.send_message(bot_username, message)

        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.metrics.record_action("send_message", elapsed_ms)
        logger.debug(f"Message sent in {elapsed_ms:.2f}ms")

        return result.id

    async def get_latest_messages(
        self,
        bot_username: str,
        limit: int = 1,
        min_id: int = 0
    ) -> list:
        """Get latest messages from a bot.

        Args:
            bot_username: Bot username
            limit: Number of messages to fetch
            min_id: Minimum message ID (for filtering)

        Returns:
            List of messages
        """
        if not bot_username.startswith('@'):
            bot_username = f'@{bot_username}'

        messages = await self.client.get_messages(
            bot_username,
            limit=limit,
            min_id=min_id
        )

        return messages

    async def is_connected(self) -> bool:
        """Check if client is connected.

        Returns:
            True if connected, False otherwise
        """
        return self.client is not None and self.client.is_connected()

    async def disconnect(self) -> None:
        """Disconnect the client."""
        if self.client:
            await self.client.disconnect()
            logger.info("Client disconnected")

    async def get_bot_entity(self, bot_username: str):
        """Get bot entity for direct operations.

        Args:
            bot_username: Bot username

        Returns:
            Bot entity
        """
        if not bot_username.startswith('@'):
            bot_username = f'@{bot_username}'

        return await self.client.get_entity(bot_username)

    def get_metrics(self) -> dict:
        """Get collected metrics.

        Returns:
            Dictionary with metrics
        """
        return self.metrics.get_statistics()
