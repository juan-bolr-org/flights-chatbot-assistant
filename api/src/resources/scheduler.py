from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from .chat import ChatManager
from typing import Generator
from pydantic import BaseModel, Field
from .logging import get_logger
from repository.user import UserRepository, create_user_repository
from repository import get_database_session

logger = get_logger("scheduler")


class SchedulerConfig(BaseModel):
    """Scheduler configuration with Pydantic validation."""
    cleanup_interval_minutes: int = Field(
        default=30, 
        ge=1, 
        le=1440, 
        description="Token cleanup interval in minutes"
    )
    job_id: str = Field(default="token_cleanup", description="Scheduler job ID")
    job_name: str = Field(
        default="Cleanup expired tokens and chat memory", 
        description="Scheduler job name"
    )


class TokenCleanupScheduler:
    """Handles cleanup of expired tokens and associated chat memory."""
    
    def __init__(self, chat_manager: ChatManager, config: SchedulerConfig = None) -> None:
        self.config: SchedulerConfig = config or SchedulerConfig()
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
        self.chat_manager: ChatManager = chat_manager
        self._is_running: bool = False
    
    async def cleanup_expired_tokens(self):
        """Remove expired tokens and cleanup associated chat memory threads."""
        logger.info("Running token cleanup task...")
        
        # Get database session using dependency function
        db_generator: Generator[Session, None, None] = get_database_session()
        db: Session = next(db_generator)
        
        try:
            # Create user repository instance
            user_repository: UserRepository = create_user_repository(db)
            
            # Find users with expired tokens
            expired_users = user_repository.find_expired_tokens()
            
            if not expired_users:
                logger.info("No expired tokens found")
                return
            
            logger.info(f"Found {len(expired_users)} users with expired tokens")
            
            # Cleanup chat memory for expired users
            cleaned_count = 0
            for user in expired_users:
                try:
                    memory = self.chat_manager.get_memory()
                    await memory.adelete_thread(f"chat_thread_{user.id}")
                    logger.debug(f"Cleaned up memory for user {user.email}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Error cleaning up memory for user {user.email}: {e}")

            logger.info(f"Successfully cleaned up {cleaned_count} expired tokens")
            
        except Exception as e:
            logger.error(f"Error during token cleanup: {e}", exc_info=True)
        finally:
            db.close()
    
    def start(self) -> None:
        """Start the cleanup scheduler."""
        if self._is_running:
            logger.warning("Token cleanup scheduler is already running")
            return
        
        # Schedule cleanup every N minutes
        self.scheduler.add_job(
            self.cleanup_expired_tokens,
            trigger=IntervalTrigger(minutes=self.config.cleanup_interval_minutes),
            id=self.config.job_id,
            name=self.config.job_name,
            replace_existing=True
        )
        
        self.scheduler.start()
        self._is_running = True
        logger.info(f"Token cleanup scheduler started (runs every {self.config.cleanup_interval_minutes} minutes)")
    
    def stop(self) -> None:
        """Stop the cleanup scheduler."""
        if not self._is_running:
            return
        
        self.scheduler.shutdown(wait=False)
        self._is_running = False
        logger.info("Token cleanup scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._is_running


# Global instance
cleanup_scheduler = None
