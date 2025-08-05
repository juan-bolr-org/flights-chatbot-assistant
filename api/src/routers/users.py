from fastapi import APIRouter, Depends, HTTPException
from schemas import UserCreate, UserLogin, Token, UserResponse
from resources.dependencies import get_crypto_manager
from resources.crypto import CryptoManager
from resources.logging import get_logger
from repository import UserRepository, create_user_repository, User
import datetime

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger("users_router")

@router.post("/register", response_model=Token)
def register(
    user: UserCreate, 
    user_repo: UserRepository = Depends(create_user_repository),
    crypto: CryptoManager = Depends(get_crypto_manager)
):
    try:
        logger.debug(f"Attempting to register user with email: {user.email}")
        
        if user_repo.exists_by_email(user.email):
            logger.warning(f"Registration failed: Email {user.email} already exists")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = crypto.get_password_hash(user.password)
        new_user = user_repo.create(
            name=user.name,
            email=user.email,
            password_hash=hashed_password,
            phone=user.phone
        )
        
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
    user_repo: UserRepository = Depends(create_user_repository),
    crypto: CryptoManager = Depends(get_crypto_manager)
):
    try:
        logger.debug(f"Login attempt for email: {user.email}")
        
        db_user = user_repo.find_by_email(user.email)
        if not db_user or not crypto.verify_password(user.password, db_user.password_hash):
            logger.warning(f"Failed login attempt for email: {user.email}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        expiration = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=60)
        updated_user = user_repo.update_token_expiration(db_user.id, expiration)
        access_token = crypto.create_access_token(data={"sub": updated_user.email})
        
        logger.info(f"Successful login for user: {user.email} (ID: {updated_user.id})")
        return UserResponse(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            phone=updated_user.phone,
            created_at=updated_user.created_at,
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
