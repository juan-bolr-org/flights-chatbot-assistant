from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.security import HTTPBearer
from repository import User
from schemas import SpeechToTextResponse
from resources.dependencies import get_current_user
from resources.logging import get_logger
from services import SpeechService, create_speech_service
from exceptions import (
    SpeechServiceNotConfiguredError,
    InvalidAudioFileError,
    SpeechRecognitionFailedError,
    NoSpeechDetectedError
)
from utils.error_handlers import api_exception_to_http_exception

router = APIRouter(prefix="/speech", tags=["speech"])
security = HTTPBearer()
logger = get_logger("speech_router")


@router.post("/to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    user: User = Depends(get_current_user),
    speech_service: SpeechService = Depends(create_speech_service)
):
    """Convert speech audio file to text using Azure Speech Services."""
    try:
        logger.debug(f"Processing speech-to-text request for user {user.id}")
        logger.debug(f"Audio file: {audio.filename}, content_type: {audio.content_type}")
        
        # Convert speech to text
        text, confidence = await speech_service.speech_to_text(audio)
        
        logger.info(f"Successfully processed speech-to-text for user {user.email}")
        # Do not log the recognized text content for privacy
        
        return SpeechToTextResponse(text=text, confidence=confidence)
        
    except (SpeechServiceNotConfiguredError, InvalidAudioFileError, 
            SpeechRecognitionFailedError, NoSpeechDetectedError) as e:
        logger.error(f"Speech-to-text error for user {user.email}: {e.message}")
        raise api_exception_to_http_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error processing speech-to-text for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Error processing speech-to-text request"
        )
