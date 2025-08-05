from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from resources.logging import get_logger
from services import HealthService, create_health_service
import datetime

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger("health_check_router")


@router.get("")
def health_check(
    health_service: HealthService = Depends(create_health_service)
) -> JSONResponse:
    """
    Health check endpoint that provides detailed information about
    application resources and their initialization status.
    """
    try:
        logger.debug("Health check requested")
        
        health_status = health_service.get_health_status()
        
        # Log the health check result and return appropriate response
        if health_status["status"] == "ok":
            logger.debug("Health check completed - all systems healthy")
            return JSONResponse(status_code=status.HTTP_200_OK, content=health_status)
        elif health_status["status"] in ["degraded", "starting"]:
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
