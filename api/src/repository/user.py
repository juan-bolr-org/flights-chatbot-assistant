from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import Depends
from resources.database import get_database_session
from models import User
import datetime


class UserRepository(ABC):
    """Abstract base class for User repository operations."""
    
    @abstractmethod
    def create(self, name: str, email: str, password_hash: str, phone: Optional[str] = None) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address."""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find a user by ID."""
        pass
    
    @abstractmethod
    def update_token_expiration(self, user_id: int, expiration: datetime.datetime) -> User:
        """Update user's token expiration time."""
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if a user exists with the given email."""
        pass
    
    @abstractmethod
    def find_expired_tokens(self) -> List[User]:
        """Find all users with expired tokens."""
        pass


class UserSqliteRepository(UserRepository):
    """SQLite implementation of UserRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str, email: str, password_hash: str, phone: Optional[str] = None) -> User:
        """Create a new user."""
        expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=60)
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            token_expiration=expiration
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address."""
        return self.db.query(User).filter(User.email == email).first()
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_token_expiration(self, user_id: int, expiration: datetime.datetime) -> User:
        """Update user's token expiration time."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        user.token_expiration = expiration
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def exists_by_email(self, email: str) -> bool:
        """Check if a user exists with the given email."""
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def find_expired_tokens(self) -> List[User]:
        """Find all users with expired tokens."""
        current_time = datetime.datetime.now(datetime.timezone.utc)
        return self.db.query(User).filter(
            User.token_expiration.isnot(None),
            User.token_expiration < current_time
        ).all()


def create_user_repository(db: Session = Depends(get_database_session)) -> UserRepository:
    """Dependency injection function to create UserRepository instance."""
    return UserSqliteRepository(db)
