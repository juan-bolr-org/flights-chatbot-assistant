from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from resources.app_resources import app_resources, AppResources
from resources.dependencies import (
    get_crypto_manager, 
    get_chat_model, 
    get_chat_memory
)
from resources.database import get_database_session
from resources.logging import get_logger
from resources.crypto import CryptoManager
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
import datetime

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger("health_check_router")


def get_app_resources() -> AppResources:
    """Dependency function to get app resources."""
    return app_resources


@router.get("")
def health_check(
    app_res: AppResources = Depends(get_app_resources),
    db: Session = Depends(get_database_session),
    crypto: CryptoManager = Depends(get_crypto_manager),
    chat_model: BaseChatModel = Depends(get_chat_model),
    chat_memory: MemorySaver = Depends(get_chat_memory)
) -> JSONResponse:
    """
    Health check endpoint that provides detailed information about
    application resources and their initialization status.
    """
    try:
        logger.debug("Health check requested")
        
        # Basic health status
        health_status = {
            "status": "ok",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "resources": {
                "initialized": app_res.is_initialized(),
                "details": {}
            }
        }
        
        # Check individual resources if app is initialized
        if app_res.is_initialized():
            # Database health
            try:
                # Test database connectivity with injected session
                db.execute(text("SELECT 1"))
                health_status["resources"]["details"]["database"] = {
                    "status": "healthy",
                    "initialized": True
                }
            except Exception as e:
                logger.warning(f"Database health check failed: {e}")
                health_status["resources"]["details"]["database"] = {
                    "status": "unhealthy",
                    "initialized": True,
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Chat system health
            try:
                # Check if chat model is available
                chat_healthy = chat_model is not None
                health_status["resources"]["details"]["chat"] = {
                    "status": "healthy" if chat_healthy else "not_initialized",
                    "initialized": chat_healthy,
                    "model_type": type(chat_model).__name__ if chat_model else None
                }
                if not chat_healthy:
                    health_status["status"] = "degraded"
            except Exception as e:
                logger.warning(f"Chat health check failed: {e}")
                health_status["resources"]["details"]["chat"] = {
                    "status": "unhealthy",
                    "initialized": False,
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Chat memory health
            try:
                # Check if chat memory is available
                memory_healthy = chat_memory is not None
                health_status["resources"]["details"]["chat_memory"] = {
                    "status": "healthy" if memory_healthy else "not_initialized",
                    "initialized": memory_healthy,
                    "memory_type": type(chat_memory).__name__ if chat_memory else None
                }
                if not memory_healthy:
                    health_status["status"] = "degraded"
            except Exception as e:
                logger.warning(f"Chat memory health check failed: {e}")
                health_status["resources"]["details"]["chat_memory"] = {
                    "status": "unhealthy",
                    "initialized": False,
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Crypto system health
            try:
                # Test crypto functionality
                crypto_healthy = crypto is not None and crypto.is_initialized()
                health_status["resources"]["details"]["crypto"] = {
                    "status": "healthy" if crypto_healthy else "not_initialized",
                    "initialized": crypto_healthy
                }
                if not crypto_healthy:
                    health_status["status"] = "degraded"
            except Exception as e:
                logger.warning(f"Crypto health check failed: {e}")
                health_status["resources"]["details"]["crypto"] = {
                    "status": "unhealthy",
                    "initialized": False,
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Scheduler health
            try:
                if app_res.scheduler:
                    scheduler_running = app_res.scheduler.is_running()
                    health_status["resources"]["details"]["scheduler"] = {
                        "status": "running" if scheduler_running else "stopped",
                        "initialized": True,
                        "running": scheduler_running
                    }
                else:
                    health_status["resources"]["details"]["scheduler"] = {
                        "status": "not_configured",
                        "initialized": False,
                        "running": False
                    }
            except Exception as e:
                logger.warning(f"Scheduler health check failed: {e}")
                health_status["resources"]["details"]["scheduler"] = {
                    "status": "unhealthy",
                    "initialized": False,
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Logging system health
            try:
                logging_healthy = app_res.logging.is_initialized()
                health_status["resources"]["details"]["logging"] = {
                    "status": "healthy" if logging_healthy else "not_initialized",
                    "initialized": logging_healthy
                }
                if not logging_healthy:
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["resources"]["details"]["logging"] = {
                    "status": "unhealthy",
                    "initialized": False,
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        
        else:
            # App resources not initialized
            health_status["status"] = "starting"
            health_status["resources"]["details"] = {
                "message": "Application resources not yet initialized"
            }
        
        # Log the health check result
        if health_status["status"] == "ok":
            logger.debug("Health check completed - all systems healthy")
            return JSONResponse(status_code=status.HTTP_200_OK, content=health_status)
        elif health_status["status"] == "degraded":
            logger.info(f"Health check completed - status: {health_status['status']}")
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status)
        elif health_status["status"] == "starting":
            logger.info(f"Health check completed - status: {health_status['status']}")
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status)
        else:
            logger.warning(f"Health check completed - unknown status: {health_status['status']}")
            return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        error_response = {
            "status": "error",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "error": str(e),
            "resources": {
                "initialized": False,
                "details": {"error": "Health check system failure"}
            }
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)
