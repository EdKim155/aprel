"""Session management for Telegram client."""

import os
from pathlib import Path
from typing import Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages Telegram session files."""

    def __init__(self, session_dir: str = "sessions"):
        """Initialize session manager.

        Args:
            session_dir: Directory to store session files
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True, parents=True)

    def get_session_path(self, session_name: str) -> str:
        """Get full path to session file.

        Args:
            session_name: Session name

        Returns:
            Full path to session file
        """
        return str(self.session_dir / session_name)

    def session_exists(self, session_name: str) -> bool:
        """Check if session file exists.

        Args:
            session_name: Session name

        Returns:
            True if session exists
        """
        session_file = self.session_dir / f"{session_name}.session"
        exists = session_file.exists()

        if exists:
            logger.info(f"Found existing session: {session_name}")
        else:
            logger.info(f"No existing session found: {session_name}")

        return exists

    def delete_session(self, session_name: str) -> bool:
        """Delete a session file.

        Args:
            session_name: Session name

        Returns:
            True if deleted, False if not found
        """
        session_file = self.session_dir / f"{session_name}.session"

        if session_file.exists():
            try:
                session_file.unlink()
                logger.info(f"Deleted session: {session_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete session: {e}")
                return False
        else:
            logger.warning(f"Session not found: {session_name}")
            return False

    def list_sessions(self) -> list:
        """List all available sessions.

        Returns:
            List of session names
        """
        sessions = []

        for session_file in self.session_dir.glob("*.session"):
            sessions.append(session_file.stem)

        return sessions

    def backup_session(self, session_name: str, backup_suffix: str = ".backup") -> bool:
        """Create a backup of a session file.

        Args:
            session_name: Session name
            backup_suffix: Suffix for backup file

        Returns:
            True if backed up successfully
        """
        session_file = self.session_dir / f"{session_name}.session"

        if not session_file.exists():
            logger.warning(f"Cannot backup non-existent session: {session_name}")
            return False

        backup_file = self.session_dir / f"{session_name}{backup_suffix}.session"

        try:
            import shutil
            shutil.copy2(session_file, backup_file)
            logger.info(f"Session backed up: {session_name} -> {backup_file.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup session: {e}")
            return False

    def restore_session(self, session_name: str, backup_suffix: str = ".backup") -> bool:
        """Restore a session from backup.

        Args:
            session_name: Session name
            backup_suffix: Suffix of backup file

        Returns:
            True if restored successfully
        """
        backup_file = self.session_dir / f"{session_name}{backup_suffix}.session"

        if not backup_file.exists():
            logger.warning(f"Backup not found: {backup_file.name}")
            return False

        session_file = self.session_dir / f"{session_name}.session"

        try:
            import shutil
            shutil.copy2(backup_file, session_file)
            logger.info(f"Session restored: {backup_file.name} -> {session_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore session: {e}")
            return False

    def get_session_info(self, session_name: str) -> Optional[dict]:
        """Get information about a session file.

        Args:
            session_name: Session name

        Returns:
            Dictionary with session info or None
        """
        session_file = self.session_dir / f"{session_name}.session"

        if not session_file.exists():
            return None

        stat = session_file.stat()

        return {
            "name": session_name,
            "path": str(session_file),
            "size_bytes": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime
        }
