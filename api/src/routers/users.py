from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, UserLogin, Token, UserResponse
from models import User
from resources.dependencies import get_database_session, get_crypto_manager
from resources.crypto import CryptoManager
from resources.logging import get_logger
import datetime

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger("users_router")

@router.post("/register", response_model=Token)
def register(
    user: UserCreate, 
    db: Session = Depends(get_database_session),
    crypto: CryptoManager = Depends(get_crypto_manager)
):
    try:
        logger.debug(f"Attempting to register user with email: {user.email}")
        
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"Registration failed: Email {user.email} already exists")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = crypto.get_password_hash(user.password)
        expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=60)
        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            phone=user.phone,
            token_expiration=expiration
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        access_token = crypto.create_access_token(data={"sub": new_user.email})
        
        logger.info(f"Successfully registered new user: {user.email} with ID: {new_user.id}")
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/login", response_model=UserResponse)
def login(
    user: UserLogin, 
    db: Session = Depends(get_database_session),
    crypto: CryptoManager = Depends(get_crypto_manager)
):
    try:
        logger.debug(f"Login attempt for email: {user.email}")
        
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not crypto.verify_password(user.password, db_user.password_hash):
            logger.warning(f"Failed login attempt for email: {user.email}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=60)
        db_user.token_expiration = expiration
        db.commit()
        db.refresh(db_user)
        access_token = crypto.create_access_token(data={"sub": db_user.email})
        
        logger.info(f"Successful login for user: {user.email} (ID: {db_user.id})")
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            phone=db_user.phone,
            created_at=db_user.created_at,
            token=Token(access_token=access_token, token_type="bearer")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login for {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during login: {str(e)}"
        )
