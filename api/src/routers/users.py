from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from schemas import UserCreate, UserLogin, Token, UserResponse
from resources.logging import get_logger
from resources.dependencies import get_current_user, get_crypto_manager
from resources.crypto import crypto_manager, CryptoManager
from services import UserService, create_user_service
from repository import User
from exceptions import ApiException
from utils.error_handlers import api_exception_to_http_exception
from constants import get_cookie_max_age_seconds

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()
logger = get_logger("users_router")

@router.post("/register", response_model=Token)
def register(
    user: UserCreate,
    response: Response,
    user_service: UserService = Depends(create_user_service),
):
    try:
        token = user_service.register(user)
        
        # Set JWT token as HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            samesite="lax",
            max_age=get_cookie_max_age_seconds()
        )
        
        return token
        
    except ApiException as e:
        logger.warning(f"Registration failed for email {user.email}: {e.message}")
        raise api_exception_to_http_exception(e)
    except Exception as e:
        logger.error(f"Error registering user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/login", response_model=UserResponse)
def login(
    user: UserLogin, 
    response: Response,
    user_service: UserService = Depends(create_user_service)
):
    try:
        user_response = user_service.login(user)
        
        # Set JWT token as HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=user_response.token.access_token,
            samesite="lax",
            max_age=get_cookie_max_age_seconds()
        )
        
        return user_response
        
    except ApiException as e:
        logger.warning(f"Failed login attempt for email: {user.email}")
        raise api_exception_to_http_exception(e)
    except Exception as e:
        logger.error(f"Error during login for {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during login: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(create_user_service)
):
    """
    Get current user information based on JWT token.
    """
    try:
        user_response = user_service.get_current_user_info(current_user, credentials.credentials)
        logger.info(f"Retrieved user info for user ID: {current_user.id}")
        return user_response
        
    except Exception as e:
        logger.error(f"Error retrieving user info for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user information: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
def refresh_token(
    response: Response,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(create_user_service),
    crypto: CryptoManager = Depends(get_crypto_manager)
):
    """
    Refresh JWT token for authenticated users with valid tokens.
    Issues a new token with configurable duration from environment.
    """
    try:
        # Create new token with configured duration
        expires_delta = timedelta(minutes=crypto.config.access_token_expire_minutes)
        new_access_token = crypto.create_access_token(
            data={"sub": current_user.email},
            expires_delta=expires_delta
        )
        
        token = Token(access_token=new_access_token, token_type="bearer")
        
        # Set the new JWT token as HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            samesite="lax",
            max_age=get_cookie_max_age_seconds()
        )
        
        logger.info(f"Token refreshed successfully for user: {current_user.email} (ID: {current_user.id})")
        return token
        
    except Exception as e:
        logger.error(f"Error refreshing token for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing token: {str(e)}"
        )

@router.post("/logout")
def logout(response: Response):
    """
    Logout endpoint that clears the JWT cookie.
    """
    try:
        # Clear the access_token cookie
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        logger.info("User logged out successfully")
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error during logout: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error during logout: {str(e)}"
        )
