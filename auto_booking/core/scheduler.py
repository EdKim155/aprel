"""Scheduler for timed booking operations."""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from ..utils.logger import get_logger

logger = get_logger(__name__)


class BookingScheduler:
    """Schedules and manages timed booking operations."""

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.scheduled_jobs = {}

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def schedule_daily_booking(
        self,
        hour: int,
        minute: int,
        callback: Callable,
        preparation_seconds: int = 60
    ) -> str:
        """Schedule daily booking at specific time.

        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
            callback: Async function to call
            preparation_seconds: Seconds before target time to start preparation

        Returns:
            Job ID
        """
        # Schedule preparation phase
        prep_minute = minute
        prep_hour = hour

        if preparation_seconds >= 60:
            prep_minute -= preparation_seconds // 60
            if prep_minute < 0:
                prep_minute += 60
                prep_hour -= 1
                if prep_hour < 0:
                    prep_hour += 24

        trigger = CronTrigger(
            hour=prep_hour,
            minute=prep_minute,
            second=60 - (preparation_seconds % 60) if preparation_seconds % 60 else 0
        )

        job = self.scheduler.add_job(
            callback,
            trigger=trigger,
            id=f"daily_booking_{hour:02d}_{minute:02d}",
            replace_existing=True
        )

        job_id = job.id
        self.scheduled_jobs[job_id] = job

        logger.info(
            f"Scheduled daily booking at {hour:02d}:{minute:02d} "
            f"(preparation starts at {prep_hour:02d}:{prep_minute:02d})"
        )

        return job_id

    def schedule_one_time_booking(
        self,
        target_datetime: datetime,
        callback: Callable,
        preparation_seconds: int = 60
    ) -> str:
        """Schedule one-time booking at specific datetime.

        Args:
            target_datetime: Target datetime for booking
            callback: Async function to call
            preparation_seconds: Seconds before target to start preparation

        Returns:
            Job ID
        """
        prep_datetime = target_datetime - timedelta(seconds=preparation_seconds)

        trigger = DateTrigger(run_date=prep_datetime)

        job = self.scheduler.add_job(
            callback,
            trigger=trigger,
            id=f"onetime_booking_{target_datetime.strftime('%Y%m%d_%H%M%S')}",
            replace_existing=True
        )

        job_id = job.id
        self.scheduled_jobs[job_id] = job

        logger.info(
            f"Scheduled one-time booking at {target_datetime.strftime('%Y-%m-%d %H:%M:%S')} "
            f"(preparation starts at {prep_datetime.strftime('%Y-%m-%d %H:%M:%S')})"
        )

        return job_id

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.scheduled_jobs:
                del self.scheduled_jobs[job_id]
            logger.info(f"Job {job_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False

    def get_scheduled_jobs(self) -> list:
        """Get list of all scheduled jobs.

        Returns:
            List of job information dictionaries
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs

    async def calculate_timing(
        self,
        target_datetime: datetime,
        preparation_seconds: int = 60,
        monitoring_start_seconds: int = 10
    ) -> dict:
        """Calculate timing parameters for booking.

        Args:
            target_datetime: Target booking time
            preparation_seconds: Preparation time in seconds
            monitoring_start_seconds: Seconds before target to start monitoring

        Returns:
            Dictionary with timing information
        """
        now = datetime.now()

        prep_start = target_datetime - timedelta(seconds=preparation_seconds)
        monitoring_start = target_datetime - timedelta(seconds=monitoring_start_seconds)

        time_to_prep = (prep_start - now).total_seconds()
        time_to_monitoring = (monitoring_start - now).total_seconds()
        time_to_target = (target_datetime - now).total_seconds()

        return {
            "current_time": now.isoformat(),
            "target_time": target_datetime.isoformat(),
            "preparation_start": prep_start.isoformat(),
            "monitoring_start": monitoring_start.isoformat(),
            "seconds_to_preparation": max(0, time_to_prep),
            "seconds_to_monitoring": max(0, time_to_monitoring),
            "seconds_to_target": max(0, time_to_target),
            "status": self._get_phase_status(time_to_prep, time_to_monitoring, time_to_target)
        }

    def _get_phase_status(
        self,
        time_to_prep: float,
        time_to_monitoring: float,
        time_to_target: float
    ) -> str:
        """Determine current phase status.

        Args:
            time_to_prep: Seconds to preparation
            time_to_monitoring: Seconds to monitoring
            time_to_target: Seconds to target time

        Returns:
            Status string
        """
        if time_to_target < 0:
            return "completed"
        elif time_to_monitoring <= 0:
            return "monitoring"
        elif time_to_prep <= 0:
            return "preparation"
        else:
            return "waiting"
