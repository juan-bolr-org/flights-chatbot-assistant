from abc import ABC, abstractmethod
from typing import Dict, Any
import os
import tempfile
import subprocess
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
from services.speech import SpeechService, create_speech_service
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
        chat_memory: MemorySaver,
        speech_service: SpeechService
    ):
        self.app_res = app_res
        self.db = db
        self.crypto = crypto
        self.chat_model = chat_model
        self.chat_memory = chat_memory
        self.speech_service = speech_service
    
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
            self._check_speech_health(health_status)
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

    def _check_speech_health(self, health_status: Dict[str, Any]) -> None:
        """Check speech service health including environment variables and ffmpeg dependency."""
        try:
            from constants import EnvironmentKeys, get_env_str
            
            # Check environment variables
            azure_speech_key = get_env_str(EnvironmentKeys.AZURE_SPEECH_KEY, "")
            azure_speech_region = get_env_str(EnvironmentKeys.AZURE_SPEECH_REGION, "")
            azure_speech_endpoint = get_env_str(EnvironmentKeys.AZURE_SPEECH_ENDPOINT, "")
            
            env_vars_status = {
                "AZURE_SPEECH_KEY": "set" if azure_speech_key else "not_set",
                "AZURE_SPEECH_REGION": "set" if azure_speech_region else "not_set", 
                "AZURE_SPEECH_ENDPOINT": "set" if azure_speech_endpoint else "not_set"
            }
            
            # Check ffmpeg availability
            ffmpeg_status = self._check_ffmpeg_availability()
            
            # Check if speech service is available
            speech_service_available = self.speech_service is not None
            
            # Determine overall speech service status
            if not azure_speech_key:
                speech_status = "not_configured"
                speech_severity = "info"  # Not critical if not configured
            elif not speech_service_available:
                speech_status = "service_unavailable"
                speech_severity = "warning"
            elif not ffmpeg_status["available"]:
                speech_status = "ffmpeg_missing"
                speech_severity = "warning"
            else:
                speech_status = "healthy"
                speech_severity = "info"
            
            health_status["resources"]["details"]["speech"] = {
                "status": speech_status,
                "initialized": speech_service_available,
                "environment_variables": env_vars_status,
                "ffmpeg": ffmpeg_status
            }
            
            # Only mark as degraded if speech was configured but has issues
            if azure_speech_key and speech_severity == "warning":
                health_status["status"] = "degraded"
                
            logger.debug(f"Speech health check: {speech_status}")
            
        except Exception as e:
            logger.warning(f"Speech health check failed: {e}")
            health_status["resources"]["details"]["speech"] = {
                "status": "unhealthy",
                "initialized": False,
                "error": str(e)
            }
            # Only mark as degraded if speech was expected to be configured
            from constants import EnvironmentKeys, get_env_str
            if get_env_str(EnvironmentKeys.AZURE_SPEECH_KEY, ""):
                health_status["status"] = "degraded"

    def _check_ffmpeg_availability(self) -> Dict[str, Any]:
        """Check if ffmpeg is available on the system."""
        try:
            # Check for ffmpeg binary
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if result.returncode == 0:
                # Extract version info from output
                version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
                return {
                    "available": True,
                    "version": version_line,
                    "status": "installed"
                }
            else:
                return {
                    "available": False,
                    "status": "command_failed",
                    "error": result.stderr or "Unknown error"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "available": False,
                "status": "timeout",
                "error": "ffmpeg command timed out"
            }
        except FileNotFoundError:
            return {
                "available": False,
                "status": "not_found",
                "error": "ffmpeg command not found"
            }
        except Exception as e:
            return {
                "available": False,
                "status": "check_failed",
                "error": str(e)
            }


def get_app_resources() -> AppResources:
    """Dependency function to get app resources."""
    return app_resources


def create_health_service(
    app_res: AppResources = Depends(get_app_resources),
    db: Session = Depends(get_database_session),
    crypto: CryptoManager = Depends(get_crypto_manager),
    chat_model: BaseChatModel = Depends(get_chat_model),
    chat_memory: MemorySaver = Depends(get_chat_memory),
    speech_service: SpeechService = Depends(create_speech_service)
) -> HealthService:
    """Dependency injection function to create HealthService instance."""
    return SystemHealthService(app_res, db, crypto, chat_model, chat_memory, speech_service)
