from .database import db_manager, DatabaseManager, DatabaseConfig
from .chat import chat_manager, ChatManager, ChatConfig
from .crypto import crypto_manager, CryptoManager, CryptoConfig
from .logging import logging_manager, LoggingManager, LoggingConfig
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field


class AppResourcesConfig(BaseModel):
    """Configuration for all application resources."""
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)
    crypto: CryptoConfig = Field(default_factory=CryptoConfig)
    auto_seed_database: bool = Field(default=True, description="Auto-seed database if empty")


class AppResources:
    """Central manager for all application resources."""
    
    def __init__(self, config: Optional[AppResourcesConfig] = None) -> None:
        self.config: AppResourcesConfig = config or AppResourcesConfig()
        self.logging: LoggingManager = logging_manager
        self.database: DatabaseManager = db_manager
        self.chat: ChatManager = chat_manager
        self.crypto: CryptoManager = crypto_manager
        self._is_initialized: bool = False
    
    def initialize_all(self) -> None:
        """Initialize all application resources in the correct order."""
        if self._is_initialized:
            # We need logging first to log this message
            self.logging.initialize()
            logger = self.logging.get_logger("app_resources")
            logger.info("Application resources already initialized.")
            return
        
        # 1. Initialize logging first (must be first!)
        self.logging.initialize()
        logger = self.logging.get_logger("app_resources")
        
        # 2. Check critical environment variables early
        self.logging.check_critical_env_vars()
        
        logger.info("Initializing application resources...")
        
        try:
            # 3. Initialize database
            logger.debug("Initializing database...")
            self.database.initialize()
            self.database.create_tables()
            
            # 4. Seed database only if empty
            if self.config.auto_seed_database:
                logger.debug("Auto-seeding database...")
                self.database.seed_database()
            
            # 5. Initialize chat components
            logger.debug("Initializing chat components...")
            self.chat.initialize()
            
            # 6. Initialize crypto components
            logger.debug("Initializing crypto components...")
            self.crypto.initialize()
            
            self._is_initialized = True
            logger.info("All application resources initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing application resources: {e}", exc_info=True)
            raise
    
    def shutdown_all(self) -> None:
        """Shutdown all application resources."""
        logger = self.logging.get_logger("app_resources")
        logger.info("Shutting down application resources...")
        logger.info("Application resources shutdown completed")
    
    def get_database_session(self) -> Session:
        """Get a database session."""
        return self.database.get_session()
    
    def is_initialized(self) -> bool:
        """Check if resources are initialized."""
        return self._is_initialized


# Global singleton instance
app_resources = AppResources()
