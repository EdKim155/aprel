"""Advanced logging configuration using loguru."""

import sys
from pathlib import Path
from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/booking_client.log",
    rotation: str = "10 MB",
    retention: str = "30 days"
) -> None:
    """Configure logging with loguru.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        rotation: Log rotation size
        retention: Log retention period
    """
    # Remove default logger
    logger.remove()

    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True, parents=True)

    # Console handler with colors
    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True
    )

    # File handler with rotation
    logger.add(
        log_file,
        level=log_level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        rotation=rotation,
        retention=retention,
        compression="zip",
        enqueue=True
    )

    # JSON file handler for structured logs
    json_log_file = log_path.parent / f"{log_path.stem}_json.log"
    logger.add(
        str(json_log_file),
        level=log_level,
        format="{message}",
        rotation=rotation,
        retention=retention,
        serialize=True,
        enqueue=True
    )

    logger.info(f"Logging initialized: level={log_level}, file={log_file}")


def get_logger(name: str):
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Convenience function for structured logging
def log_booking_attempt(
    session_id: str,
    sms_detected_at: str,
    target_shipment: str,
    sms_to_start_ms: float,
    start_to_select_ms: float,
    select_to_confirm_ms: float,
    total_time_ms: float,
    result: str,
    position_in_queue: int = None
) -> None:
    """Log a booking attempt with structured data.

    Args:
        session_id: Unique session ID
        sms_detected_at: Timestamp when SMS was detected
        target_shipment: Name of target shipment
        sms_to_start_ms: Time from SMS to /start
        start_to_select_ms: Time from /start to selection
        select_to_confirm_ms: Time from selection to confirmation
        total_time_ms: Total time taken
        result: Result status
        position_in_queue: Position in queue (if available)
    """
    logger.info(
        "Booking attempt completed",
        extra={
            "session_id": session_id,
            "action": "booking_attempt",
            "details": {
                "sms_detected_at": sms_detected_at,
                "target_shipment": target_shipment,
                "sms_to_start_ms": sms_to_start_ms,
                "start_to_select_ms": start_to_select_ms,
                "select_to_confirm_ms": select_to_confirm_ms,
                "total_time_ms": total_time_ms,
                "result": result,
                "position_in_queue": position_in_queue
            }
        }
    )
