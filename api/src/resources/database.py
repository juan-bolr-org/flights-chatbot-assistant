from collections.abc import Generator
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Engine
from typing import Optional
from pydantic import BaseModel, Field

from models import Base, User
from .logging import get_logger

logger = get_logger("database")


class DatabaseConfig(BaseModel):
    """Database configuration with Pydantic validation."""
    database_url: str = Field(default="sqlite:///./flights.db", description="Main database URL")
    check_same_thread: bool = Field(default=False, description="SQLite thread safety setting")
    autocommit: bool = Field(default=False, description="SQLAlchemy autocommit setting")
    autoflush: bool = Field(default=False, description="SQLAlchemy autoflush setting")


class DatabaseManager:
    """Manages database connection, initialization, and seeding."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None) -> None:
        self.config: DatabaseConfig = config or DatabaseConfig()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker[Session]] = None
        self._is_initialized: bool = False
    
    def initialize(self) -> None:
        """Initialize the database engine and session factory."""
        if self._is_initialized:
            return
            
        logger.debug(f"Initializing database with URL: {self.config.database_url}")
        self.engine = create_engine(
            self.config.database_url, 
            connect_args={"check_same_thread": self.config.check_same_thread}
        )
        self.SessionLocal = sessionmaker(
            autocommit=self.config.autocommit, 
            autoflush=self.config.autoflush, 
            bind=self.engine
        )
        self._is_initialized = True
        logger.info("Database manager initialized successfully")
    
    def create_tables(self) -> None:
        """Create all database tables."""
        if not self._is_initialized:
            self.initialize()
        logger.debug("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def get_session(self) -> Session:
        """Get a database session."""
        if not self._is_initialized:
            self.initialize()
        return self.SessionLocal()
    
    def is_database_empty(self) -> bool:
        """Check if the database is empty (no users exist)."""
        db = self.get_session()
        try:
            user_count = db.query(User).count()
            logger.debug(f"Database user count: {user_count}")
            return user_count == 0
        except Exception as e:
            logger.error(f"Error checking if database is empty: {e}")
            raise
        finally:
            db.close()
    
    def seed_database(self) -> None:
        """Seed the database with initial data only if it's empty."""
        if not self.is_database_empty():
            logger.info("Database already contains data. Skipping seeding")
            return
        
        logger.info("Database is empty. Seeding with initial data...")
        try:
            from .seed_data import DataSeeder
            seeder = DataSeeder(self)
            seeder.seed_all()
            logger.info("Database seeding completed successfully")
        except Exception as e:
            logger.error(f"Error during database seeding: {e}", exc_info=True)
            raise


# Global instance - Singleton pattern
db_manager = DatabaseManager()

def get_database_session() -> Generator[Session, None, None]:
    """Dependency function to get a database session."""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()