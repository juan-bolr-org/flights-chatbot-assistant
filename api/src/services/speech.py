from abc import ABC, abstractmethod
import os
import tempfile
import azure.cognitiveservices.speech as speechsdk
from fastapi import UploadFile
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from resources.logging import get_logger
from exceptions import (
    SpeechServiceNotConfiguredError,
    InvalidAudioFileError, 
    SpeechRecognitionFailedError,
    NoSpeechDetectedError
)

logger = get_logger("speech_service")


class SpeechService(ABC):
    """Abstract base class for Speech service operations."""
    
    @abstractmethod
    async def speech_to_text(self, audio_file: UploadFile) -> tuple[str, float]:
        """Convert audio file to text using speech recognition service."""
        pass


class AzureSpeechService(SpeechService):
    """Implementation of SpeechService using Azure Cognitive Services."""
    
    def __init__(self):
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        self.speech_endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")
        
        if not self.speech_key:
            logger.warning("Azure Speech key not configured")
    
    def _convert_to_wav(self, input_file_path: str, output_file_path: str) -> None:
        """Convert audio file to WAV format using pydub."""
        try:
            logger.debug(f"Converting audio from {input_file_path} to WAV format")
            
            # Load audio file (supports multiple formats including webm)
            audio = AudioSegment.from_file(input_file_path)
            
            logger.debug(f"Original audio - Duration: {len(audio)}ms, Channels: {audio.channels}, "
                        f"Frame rate: {audio.frame_rate}Hz")
            
            # Convert to WAV with speech recognition optimized settings
            audio = audio.set_frame_rate(16000)  # 16kHz sample rate for speech
            audio = audio.set_channels(1)        # Mono channel
            audio = audio.set_sample_width(2)    # 16-bit
            
            # Export as WAV
            audio.export(output_file_path, format="wav")
            logger.debug("Successfully converted audio to WAV format")
            
        except CouldntDecodeError as e:
            logger.error(f"Could not decode audio file: {e}")
            raise InvalidAudioFileError("Unsupported audio format or corrupted file")
        except FileNotFoundError as e:
            error_msg = str(e)
            logger.error(f"File not found: {e}")
            
            # Check if it's ffmpeg/ffprobe missing
            if "ffprobe" in error_msg or "ffmpeg" in error_msg:
                raise SpeechRecognitionFailedError(
                    "Audio conversion failed: ffmpeg is not available on the system"
                )
            else:
                raise SpeechRecognitionFailedError(f"Input file not found: {str(e)}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error converting audio to WAV: {e}")
            
            # Check if it's ffmpeg/ffprobe missing
            if "ffprobe" in error_msg or "ffmpeg" in error_msg:
                raise SpeechRecognitionFailedError(
                    "Audio conversion failed: ffmpeg is not available on the system"
                )
            else:
                raise SpeechRecognitionFailedError(f"Audio conversion failed: {str(e)}")
    
    async def speech_to_text(self, audio_file: UploadFile) -> tuple[str, float]:
        """Convert audio file to text using Azure Speech Service."""
        logger.debug(f"Processing speech-to-text for file: {audio_file.filename} ({audio_file.content_type})")
        
        if not self.speech_key:
            logger.error("Azure Speech key not configured")
            raise SpeechServiceNotConfiguredError()
        
        # Validate file type - now support both audio/* and specific formats
        if not audio_file.content_type:
            logger.error("No content type specified in uploaded file")
            raise InvalidAudioFileError("No content type specified")
        
        # Accept audio/* content types and some video/* for webm
        acceptable_types = ['audio/', 'video/webm', 'video/ogg']
        is_acceptable = any(audio_file.content_type.startswith(type_prefix) for type_prefix in acceptable_types)
        
        if not is_acceptable:
            logger.error(f"Unsupported content type: {audio_file.content_type}")
            raise InvalidAudioFileError(audio_file.content_type)
            
        temp_input_path = None
        temp_wav_path = None
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as temp_input_file:
                content = await audio_file.read()
                
                if len(content) == 0:
                    logger.error("Uploaded file is empty")
                    raise InvalidAudioFileError("Uploaded file is empty")
                
                temp_input_file.write(content)
                temp_input_path = temp_input_file.name
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
                temp_wav_path = temp_wav_file.name
            
            # Convert to WAV if not already WAV
            if audio_file.content_type == 'audio/wav':
                # If already WAV, just copy the content
                with open(temp_wav_path, 'wb') as wav_file:
                    wav_file.write(content)
                logger.debug("Input file is already WAV format")
            else:
                # Convert to WAV
                logger.debug(f"Converting {audio_file.content_type} to WAV format")
                self._convert_to_wav(temp_input_path, temp_wav_path)
            
            # Configure speech service
            speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                endpoint=self.speech_endpoint
            )
            speech_config.speech_recognition_language = "en-US"
            
            # Create audio config from WAV file
            audio_config = speechsdk.audio.AudioConfig(filename=temp_wav_path)
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )

            # Perform recognition
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                confidence = getattr(result, 'confidence', 1.0)
                logger.info("Speech successfully recognized")
                return result.text, confidence
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech detected in audio file")
                raise NoSpeechDetectedError()
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                logger.error(f"Speech recognition canceled: {cancellation_details.reason}")
                if cancellation_details.error_details:
                    logger.error(f"Error details: {cancellation_details.error_details}")
                raise SpeechRecognitionFailedError(f"Recognition canceled: {cancellation_details.reason}")
            else:
                logger.error(f"Unexpected recognition result reason: {result.reason}")
                raise SpeechRecognitionFailedError(f"Unexpected result: {result.reason}")
                
        except (SpeechServiceNotConfiguredError, InvalidAudioFileError, 
                NoSpeechDetectedError, SpeechRecognitionFailedError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in speech recognition: {e}", exc_info=True)
            raise SpeechRecognitionFailedError(str(e))
        finally:
            # Clean up temporary files
            for temp_path in [temp_input_path, temp_wav_path]:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.warning(f"Failed to cleanup temp file {temp_path}: {e}")


def create_speech_service() -> SpeechService:
    """Factory function to create appropriate speech service instance."""
    return AzureSpeechService()
        
