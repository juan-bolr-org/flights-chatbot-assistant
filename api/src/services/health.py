from abc import ABC, abstractmethod
from typing import Dict, Any
from fastapi import Depends
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

logger = get_logger("health_service")


class HealthService(ABC):
    """Abstract base class for Health service operations."""
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of all application components."""
        pass


class SystemHealthService(HealthService):
    """Implementation of HealthService with system health checks."""
    
    def __init__(
        self, 
        app_res: AppResources,
        db: Session,
        crypto: CryptoManager,
        chat_model: BaseChatModel,
        chat_memory: MemorySaver
    ):
        self.app_res = app_res
        self.db = db
        self.crypto = crypto
        self.chat_model = chat_model
        self.chat_memory = chat_memory
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of all application components."""
        logger.debug("Performing health check")
        
        # Basic health status
        health_status = {
            "status": "ok",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "resources": {
                "initialized": self.app_res.is_initialized(),
                "details": {}
            }
        }
        
        # Check individual resources if app is initialized
        if self.app_res.is_initialized():
            self._check_database_health(health_status)
            self._check_chat_health(health_status)
            self._check_chat_memory_health(health_status)
            self._check_crypto_health(health_status)
            self._check_scheduler_health(health_status)
            self._check_logging_health(health_status)
        else:
            # App resources not initialized
            health_status["status"] = "starting"
            health_status["resources"]["details"] = {
                "message": "Application resources not yet initialized"
            }
        
        logger.debug(f"Health check completed with status: {health_status['status']}")
        return health_status
    
    def _check_database_health(self, health_status: Dict[str, Any]) -> None:
        """Check database connectivity and health."""
        try:
            # Test database connectivity with injected session
            self.db.execute(text("SELECT 1"))
            health_status["resources"]["details"]["database"] = {
                "status": "healthy",
                "initialized": True
            }
            logger.debug("Database health check: healthy")
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            health_status["resources"]["details"]["database"] = {
                "status": "unhealthy",
                "initialized": True,
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    def _check_chat_health(self, health_status: Dict[str, Any]) -> None:
        """Check chat model health."""
        try:
            # Check if chat model is available
            chat_healthy = self.chat_model is not None
            health_status["resources"]["details"]["chat"] = {
                "status": "healthy" if chat_healthy else "not_initialized",
                "initialized": chat_healthy,
                "model_type": type(self.chat_model).__name__ if self.chat_model else None
            }
            if not chat_healthy:
                health_status["status"] = "degraded"
            logger.debug(f"Chat health check: {'healthy' if chat_healthy else 'not_initialized'}")
        except Exception as e:
            logger.warning(f"Chat health check failed: {e}")
            health_status["resources"]["details"]["chat"] = {
                "status": "unhealthy",
                "initialized": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    def _check_chat_memory_health(self, health_status: Dict[str, Any]) -> None:
        """Check chat memory health."""
        try:
            # Check if chat memory is available
            memory_healthy = self.chat_memory is not None
            health_status["resources"]["details"]["chat_memory"] = {
                "status": "healthy" if memory_healthy else "not_initialized",
                "initialized": memory_healthy,
                "memory_type": type(self.chat_memory).__name__ if self.chat_memory else None
            }
            if not memory_healthy:
                health_status["status"] = "degraded"
            logger.debug(f"Chat memory health check: {'healthy' if memory_healthy else 'not_initialized'}")
        except Exception as e:
            logger.warning(f"Chat memory health check failed: {e}")
            health_status["resources"]["details"]["chat_memory"] = {
                "status": "unhealthy",
                "initialized": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    def _check_crypto_health(self, health_status: Dict[str, Any]) -> None:
        """Check crypto system health."""
        try:
            # Test crypto functionality
            crypto_healthy = self.crypto is not None and self.crypto.is_initialized()
            health_status["resources"]["details"]["crypto"] = {
                "status": "healthy" if crypto_healthy else "not_initialized",
                "initialized": crypto_healthy
            }
            if not crypto_healthy:
                health_status["status"] = "degraded"
            logger.debug(f"Crypto health check: {'healthy' if crypto_healthy else 'not_initialized'}")
        except Exception as e:
            logger.warning(f"Crypto health check failed: {e}")
            health_status["resources"]["details"]["crypto"] = {
                "status": "unhealthy",
                "initialized": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    def _check_scheduler_health(self, health_status: Dict[str, Any]) -> None:
        """Check scheduler health."""
        try:
            if self.app_res.scheduler:
                scheduler_running = self.app_res.scheduler.is_running()
                health_status["resources"]["details"]["scheduler"] = {
                    "status": "running" if scheduler_running else "stopped",
                    "initialized": True,
                    "running": scheduler_running
                }
                logger.debug(f"Scheduler health check: {'running' if scheduler_running else 'stopped'}")
            else:
                health_status["resources"]["details"]["scheduler"] = {
                    "status": "not_configured",
                    "initialized": False,
                    "running": False
                }
                logger.debug("Scheduler health check: not_configured")
        except Exception as e:
            logger.warning(f"Scheduler health check failed: {e}")
            health_status["resources"]["details"]["scheduler"] = {
                "status": "unhealthy",
                "initialized": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    def _check_logging_health(self, health_status: Dict[str, Any]) -> None:
        """Check logging system health."""
        try:
            logging_healthy = self.app_res.logging.is_initialized()
            health_status["resources"]["details"]["logging"] = {
                "status": "healthy" if logging_healthy else "not_initialized",
                "initialized": logging_healthy
            }
            if not logging_healthy:
                health_status["status"] = "degraded"
            logger.debug(f"Logging health check: {'healthy' if logging_healthy else 'not_initialized'}")
        except Exception as e:
            health_status["resources"]["details"]["logging"] = {
                "status": "unhealthy",
                "initialized": False,
                "error": str(e)
            }
            health_status["status"] = "degraded"


def get_app_resources() -> AppResources:
    """Dependency function to get app resources."""
    return app_resources


def create_health_service(
    app_res: AppResources = Depends(get_app_resources),
    db: Session = Depends(get_database_session),
    crypto: CryptoManager = Depends(get_crypto_manager),
    chat_model: BaseChatModel = Depends(get_chat_model),
    chat_memory: MemorySaver = Depends(get_chat_memory)
) -> HealthService:
    """Dependency injection function to create HealthService instance."""
    return SystemHealthService(app_res, db, crypto, chat_model, chat_memory)
