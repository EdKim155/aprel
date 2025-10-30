"""Configuration settings loader."""

import os
from typing import List, Optional
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, validator


class TelegramConfig(BaseModel):
    """Telegram API configuration."""
    api_id: int
    api_hash: str
    phone: str
    session_name: str = "auto_booking_session"


class BotConfig(BaseModel):
    """Bot-specific configuration."""
    username: str
    sms_trigger_text: str = "Появились новые перевозки"


class BookingConfig(BaseModel):
    """Booking operation configuration."""
    target_time: str = "11:30:00"
    preparation_time_seconds: int = 60
    monitoring_start_seconds: int = 10
    sms_reaction_time_ms: int = 50

    @validator('target_time')
    def validate_time_format(cls, v):
        """Validate time format."""
        from datetime import datetime
        try:
            datetime.strptime(v, '%H:%M:%S')
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM:SS format')


class TargetShipment(BaseModel):
    """Target shipment configuration."""
    type: str
    cities: List[str]
    priority: int = 1


class PerformanceConfig(BaseModel):
    """Performance parameters."""
    sms_to_start_ms: int = 50
    start_to_select_ms: int = 50
    select_to_confirm_ms: int = 30
    max_retries: int = 3
    connection_timeout: int = 10
    polling_interval_ms: int = 30


class NotificationConfig(BaseModel):
    """Notification settings."""
    telegram_notify: bool = True
    notify_user_id: Optional[int] = None
    sound_alert: bool = True


class Settings(BaseModel):
    """Main settings container."""
    telegram: TelegramConfig
    bot: BotConfig
    booking: BookingConfig
    targets: List[TargetShipment]
    performance: PerformanceConfig
    notifications: NotificationConfig

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


def load_settings(config_path: str = "config.yaml") -> Settings:
    """Load settings from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Settings object

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please create config.yaml based on config.example.yaml"
        )

    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    # Override with environment variables if present
    if 'TELEGRAM_API_ID' in os.environ:
        config_data.setdefault('telegram', {})['api_id'] = int(os.environ['TELEGRAM_API_ID'])

    if 'TELEGRAM_API_HASH' in os.environ:
        config_data.setdefault('telegram', {})['api_hash'] = os.environ['TELEGRAM_API_HASH']

    if 'TELEGRAM_PHONE' in os.environ:
        config_data.setdefault('telegram', {})['phone'] = os.environ['TELEGRAM_PHONE']

    if 'BOT_USERNAME' in os.environ:
        config_data.setdefault('bot', {})['username'] = os.environ['BOT_USERNAME']

    try:
        settings = Settings(**config_data)
        return settings
    except Exception as e:
        raise ValueError(f"Invalid configuration: {e}")


def create_example_config(output_path: str = "config.example.yaml") -> None:
    """Create an example configuration file.

    Args:
        output_path: Path where to create the example file
    """
    example_config = {
        "telegram": {
            "api_id": 12345678,
            "api_hash": "your_api_hash_here",
            "phone": "+7XXXXXXXXXX",
            "session_name": "auto_booking_session"
        },
        "bot": {
            "username": "your_bot_username",
            "sms_trigger_text": "Появились новые перевозки"
        },
        "booking": {
            "target_time": "11:30:00",
            "preparation_time_seconds": 60,
            "monitoring_start_seconds": 10,
            "sms_reaction_time_ms": 50
        },
        "targets": [
            {
                "type": "прямые",
                "cities": ["Челябинск", "Екатеринбург"],
                "priority": 1
            },
            {
                "type": "магистральные",
                "cities": ["Москва", "Казань"],
                "priority": 2
            }
        ],
        "performance": {
            "sms_to_start_ms": 50,
            "start_to_select_ms": 50,
            "select_to_confirm_ms": 30,
            "max_retries": 3,
            "connection_timeout": 10,
            "polling_interval_ms": 30
        },
        "notifications": {
            "telegram_notify": True,
            "notify_user_id": None,
            "sound_alert": True
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(example_config, f, allow_unicode=True, sort_keys=False)

    print(f"Example configuration created at: {output_path}")
