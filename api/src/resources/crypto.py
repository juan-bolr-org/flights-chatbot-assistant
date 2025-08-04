from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta
import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field
import os
from .logging import get_logger

logger = get_logger("crypto")


class CryptoConfig(BaseModel):
    """Cryptography configuration with Pydantic validation."""
    secret_key: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", "please_guys_do_not_forget_to_set_a_secret_key"),
        description="Secret key for JWT encoding"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=60, 
        ge=1, 
        le=10080,  # Max 7 days
        description="Access token expiration time in minutes"
    )
    password_schemes: list[str] = Field(
        default=["sha256_crypt"], 
        description="Password hashing schemes"
    )


class CryptoManager:
    """Manages cryptographic operations for passwords and tokens."""
    
    def __init__(self, config: Optional[CryptoConfig] = None) -> None:
        self.config: CryptoConfig = config or CryptoConfig()
        self.pwd_context: CryptContext = CryptContext(schemes=self.config.password_schemes)
        self._is_initialized: bool = False
    
    def initialize(self) -> None:
        """Initialize the crypto manager."""
        if self._is_initialized:
            return
        
        # This validation is now handled in the main startup check
        # But we'll keep a debug log here
        if not self.config.secret_key or self.config.secret_key == "please_guys_do_not_forget_to_set_a_secret_key":
            logger.debug("Using default secret key (already warned during startup)")
        
        self._is_initialized = True
        logger.info("Crypto manager initialized successfully")
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password using the configured context."""
        if not self._is_initialized:
            self.initialize()
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if not self._is_initialized:
            self.initialize()
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        data: Dict[str, str], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        if not self._is_initialized:
            self.initialize()
        
        to_encode = data.copy()
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.config.access_token_expire_minutes)
        
        expire = datetime.datetime.now(datetime.UTC) + expires_delta
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, str]:
        """Decode and validate a JWT token."""
        if not self._is_initialized:
            self.initialize()
        
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")
    
    def get_token_subject(self, token: str) -> Optional[str]:
        """Extract the subject (user identifier) from a token."""
        try:
            payload = self.decode_token(token)
            return payload.get("sub")
        except ValueError:
            return None


# Global instance - Singleton pattern
crypto_manager = CryptoManager()
