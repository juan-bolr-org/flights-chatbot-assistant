from fastapi import APIRouter, Depends, HTTPException
from schemas import UserCreate, UserLogin, Token, UserResponse
from resources.logging import get_logger
from services import UserService, create_user_service
from exceptions import ApiException
from utils.error_handlers import api_exception_to_http_exception

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger("users_router")

@router.post("/register", response_model=Token)
def register(
    user: UserCreate, 
    user_service: UserService = Depends(create_user_service)
):
    try:
        token = user_service.register(user)
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
    user_service: UserService = Depends(create_user_service)
):
    try:
        user_response = user_service.login(user)
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
