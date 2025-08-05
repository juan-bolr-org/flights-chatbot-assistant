from abc import ABC, abstractmethod
from fastapi import Depends
from schemas import UserCreate, UserLogin, Token, UserResponse
from resources.crypto import CryptoManager
from resources.dependencies import get_crypto_manager
from repository import UserRepository, create_user_repository
from resources.logging import get_logger
from exceptions import EmailAlreadyExistsError, InvalidCredentialsError
import datetime

logger = get_logger("user_service")


class UserService(ABC):
    """Abstract base class for User service operations."""
    
    @abstractmethod
    def register(self, user: UserCreate) -> Token:
        """Register a new user."""
        pass
    
    @abstractmethod
    def login(self, user: UserLogin) -> UserResponse:
        """Login a user."""
        pass


class UserBusinessService(UserService):
    """Implementation of UserService with business logic."""
    
    def __init__(self, user_repo: UserRepository, crypto: CryptoManager):
        self.user_repo = user_repo
        self.crypto = crypto
    
    def register(self, user: UserCreate) -> Token:
        """Register a new user."""
        logger.debug(f"Attempting to register user with email: {user.email}")
        
        if self.user_repo.exists_by_email(user.email):
            logger.warning(f"Registration failed: Email {user.email} already exists")
            raise EmailAlreadyExistsError(user.email)
        
        hashed_password = self.crypto.get_password_hash(user.password)
        new_user = self.user_repo.create(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            phone=user.phone
        )
        
        access_token = self.crypto.create_access_token(data={"sub": new_user.email})
        
        logger.info(f"Successfully registered new user: {user.email} with ID: {new_user.id}")
        return Token(access_token=access_token, token_type="bearer")
    
    def login(self, user: UserLogin) -> UserResponse:
        """Login a user."""
        logger.debug(f"Login attempt for email: {user.email}")

        if len(user.password) < 8:
            logger.warning(f"Login failed: Password too short for email {user.email}")
            raise InvalidCredentialsError()
        
        db_user = self.user_repo.find_by_email(user.email)
        if not db_user or not self.crypto.verify_password(user.password, db_user.password_hash):
            logger.warning(f"Failed login attempt for email: {user.email}")
            raise InvalidCredentialsError()
        
        expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60)
        updated_user = self.user_repo.update_token_expiration(db_user.id, expiration)
        access_token = self.crypto.create_access_token(data={"sub": updated_user.email})
        
        logger.info(f"Successful login for user: {user.email} (ID: {updated_user.id})")
        return UserResponse(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            phone=updated_user.phone,
            created_at=updated_user.created_at,
            token=Token(access_token=access_token, token_type="bearer")
        )


def create_user_service(
    user_repo: UserRepository = Depends(create_user_repository),
    crypto: CryptoManager = Depends(get_crypto_manager)
) -> UserService:
    """Dependency injection function to create UserService instance."""
    return UserBusinessService(user_repo, crypto)
