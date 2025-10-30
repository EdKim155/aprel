"""Automated Telegram booking client.

This package provides an automated client for ultra-fast booking
through Telegram bots using the Telegram Client API.
"""

__version__ = "1.0.0"
__author__ = "Auto Booking Team"

from .core import BookingClient, BotHandler, ButtonClicker, BookingScheduler
from .config import Settings, load_settings, SessionManager
from .utils import get_logger, setup_logging, MetricsCollector, Notifier

__all__ = [
    'BookingClient',
    'BotHandler',
    'ButtonClicker',
    'BookingScheduler',
    'Settings',
    'load_settings',
    'SessionManager',
    'get_logger',
    'setup_logging',
    'MetricsCollector',
    'Notifier',
]
