"""
Tests for SpeechService - Service Layer
Tests mock Azure Speech SDK and audio processing to focus on service logic.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock, mock_open
import tempfile
import os
from fastapi import UploadFile

# Add src to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import azure speechsdk for constants
try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    # For tests, create a mock speechsdk module with necessary constants
    speechsdk = Mock()
    speechsdk.ResultReason = Mock()
    speechsdk.ResultReason.RecognizedSpeech = "RecognizedSpeech"
    speechsdk.ResultReason.NoMatch = "NoMatch"
    speechsdk.ResultReason.Canceled = "Canceled"

from services.speech import AzureSpeechService
from exceptions import (
    SpeechServiceNotConfiguredError,
    InvalidAudioFileError,
    SpeechRecognitionFailedError,
    NoSpeechDetectedError
)


class TestAzureSpeechService:
    """Test suite for AzureSpeechService with mocked dependencies."""
    
    @pytest.fixture
    def mock_upload_file(self):
        """Create mock upload file."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test_audio.wav"
        mock_file.content_type = "audio/wav"
        mock_file.read = AsyncMock(return_value=b"fake_audio_data")
        return mock_file
    
    @pytest.fixture
    def mock_webm_upload_file(self):
        """Create mock webm upload file."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test_audio.webm"
        mock_file.content_type = "video/webm"
        mock_file.read = AsyncMock(return_value=b"fake_webm_data")
        return mock_file
    
    @pytest.fixture
    def speech_service_configured(self):
        """Create speech service with mocked environment variables."""
        with patch.dict(os.environ, {
            'AZURE_SPEECH_KEY': 'test_key',
            'AZURE_SPEECH_REGION': 'eastus'
        }):
            return AzureSpeechService()
    
    @pytest.fixture
    def speech_service_not_configured(self):
        """Create speech service without environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            return AzureSpeechService()
    
    # ===== POSITIVE TESTS =====
    
    @pytest.mark.asyncio
    async def test_speech_to_text_success_wav(self, speech_service_configured, mock_upload_file):
        """Test successful speech to text conversion with WAV file."""
        with patch('azure.cognitiveservices.speech.SpeechConfig') as mock_speech_config, \
             patch('azure.cognitiveservices.speech.SpeechRecognizer') as mock_recognizer_class, \
             patch('azure.cognitiveservices.speech.audio.AudioConfig') as mock_audio_config, \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file:
            
            # Setup mocks
            mock_config = Mock()
            mock_speech_config.return_value = mock_config
            
            mock_recognizer = Mock()
            mock_recognizer_class.return_value = mock_recognizer
            
            # Mock recognition result with correct ResultReason
            mock_result = Mock()
            mock_result.text = "Hello world"
            mock_result.reason = speechsdk.ResultReason.RecognizedSpeech
            mock_result.confidence = 0.95  # Set confidence as a float
            mock_recognizer.recognize_once.return_value = mock_result
            
            # Mock temp file context manager
            mock_temp_file_obj = Mock()
            mock_temp_file_obj.name = "/tmp/test_audio.wav"
            mock_temp_file_obj.write = Mock()
            mock_temp_file_obj.flush = Mock()
            mock_temp_file.return_value.__enter__.return_value = mock_temp_file_obj
            mock_temp_file.return_value.__exit__.return_value = None
            
            # Mock audio config
            mock_audio_config.return_value = Mock()
            
            # Execute
            result_text, confidence = await speech_service_configured.speech_to_text(mock_upload_file)
        
        # Verify
        assert result_text == "Hello world"
        assert confidence > 0.0
        mock_upload_file.read.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_speech_to_text_success_webm(self, speech_service_configured, mock_webm_upload_file):
        """Test successful speech to text conversion with WebM file."""
        with patch('azure.cognitiveservices.speech.SpeechConfig') as mock_speech_config, \
             patch('azure.cognitiveservices.speech.SpeechRecognizer') as mock_recognizer_class, \
             patch('azure.cognitiveservices.speech.audio.AudioConfig') as mock_audio_config, \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file, \
             patch.object(speech_service_configured, '_convert_to_wav') as mock_convert:
            
            # Setup mocks
            mock_config = Mock()
            mock_speech_config.return_value = mock_config
            
            mock_recognizer = Mock()
            mock_recognizer_class.return_value = mock_recognizer
            
            # Mock recognition result with correct ResultReason
            mock_result = Mock()
            mock_result.text = "Hello from webm"
            mock_result.reason = speechsdk.ResultReason.RecognizedSpeech
            mock_result.confidence = 0.90  # Set confidence as a float
            mock_recognizer.recognize_once.return_value = mock_result
            
            # Mock temp files context manager
            mock_temp_file_obj = Mock()
            mock_temp_file_obj.name = "/tmp/test_audio.webm"
            mock_temp_file_obj.write = Mock()
            mock_temp_file_obj.flush = Mock()
            mock_temp_file.return_value.__enter__.return_value = mock_temp_file_obj
            mock_temp_file.return_value.__exit__.return_value = None
            
            # Mock audio config
            mock_audio_config.return_value = Mock()
            
            # Execute
            result_text, confidence = await speech_service_configured.speech_to_text(mock_webm_upload_file)
            
            # Verify
            assert result_text == "Hello from webm"
            assert confidence > 0.0
            mock_convert.assert_called_once()
    
    def test_convert_to_wav_success(self, speech_service_configured):
        """Test successful audio conversion to WAV."""
        with patch('pydub.AudioSegment.from_file') as mock_from_file, \
             patch('pydub.AudioSegment.export') as mock_export:
            
            # Setup mock audio segment
            mock_audio = Mock()
            mock_audio.__len__ = Mock(return_value=30000)  # 30 seconds in milliseconds
            mock_audio.channels = 2
            mock_audio.frame_rate = 44100
            mock_audio.set_frame_rate.return_value = mock_audio
            mock_audio.set_channels.return_value = mock_audio
            mock_audio.set_sample_width.return_value = mock_audio
            mock_from_file.return_value = mock_audio
            
            # Execute
            speech_service_configured._convert_to_wav("/tmp/input.webm", "/tmp/output.wav")
            
            # Verify
            mock_from_file.assert_called_once_with("/tmp/input.webm")
            mock_audio.set_frame_rate.assert_called_once_with(16000)
            mock_audio.set_channels.assert_called_once_with(1)
            mock_audio.set_sample_width.assert_called_once_with(2)
            mock_audio.export.assert_called_once_with("/tmp/output.wav", format="wav")
    
    # ===== NEGATIVE TESTS =====
    
    @pytest.mark.asyncio
    async def test_speech_to_text_not_configured(self, speech_service_not_configured, mock_upload_file):
        """Test speech to text when service is not configured."""
        with pytest.raises(SpeechServiceNotConfiguredError):
            await speech_service_not_configured.speech_to_text(mock_upload_file)
    
    @pytest.mark.asyncio
    async def test_speech_to_text_invalid_content_type(self, speech_service_configured):
        """Test speech to text with invalid content type."""
        mock_file = Mock(spec=UploadFile)
        mock_file.content_type = "text/plain"
        mock_file.filename = "test.txt"
        
        with pytest.raises(InvalidAudioFileError) as exc_info:
            await speech_service_configured.speech_to_text(mock_file)
        
        assert "File must be a valid audio file" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_speech_to_text_no_content_type(self, speech_service_configured):
        """Test speech to text with no content type."""
        mock_file = Mock(spec=UploadFile)
        mock_file.content_type = None
        mock_file.filename = "test.wav"
        
        with pytest.raises(InvalidAudioFileError) as exc_info:
            await speech_service_configured.speech_to_text(mock_file)
        
        assert "File must be a valid audio file" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_speech_to_text_no_speech_detected(self, speech_service_configured, mock_upload_file):
        """Test speech to text when no speech is detected."""
        with patch('azure.cognitiveservices.speech.SpeechConfig'), \
             patch('azure.cognitiveservices.speech.SpeechRecognizer') as mock_recognizer_class, \
             patch('azure.cognitiveservices.speech.audio.AudioConfig') as mock_audio_config, \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file:
            
            # Setup mocks
            mock_recognizer = Mock()
            mock_recognizer_class.return_value = mock_recognizer
            
            # Mock no speech result with correct ResultReason
            mock_result = Mock()
            mock_result.text = ""
            mock_result.reason = speechsdk.ResultReason.NoMatch
            mock_recognizer.recognize_once.return_value = mock_result
            
            # Mock temp file context manager  
            mock_temp_file_obj = Mock()
            mock_temp_file_obj.name = "/tmp/test_audio.wav"
            mock_temp_file_obj.write = Mock()
            mock_temp_file_obj.flush = Mock()
            mock_temp_file.return_value.__enter__.return_value = mock_temp_file_obj
            mock_temp_file.return_value.__exit__.return_value = None
            
            # Mock audio config
            mock_audio_config.return_value = Mock()
            
            with pytest.raises(NoSpeechDetectedError):
                await speech_service_configured.speech_to_text(mock_upload_file)
    
    @pytest.mark.asyncio
    async def test_speech_to_text_recognition_failed(self, speech_service_configured, mock_upload_file):
        """Test speech to text when recognition fails."""
        with patch('azure.cognitiveservices.speech.SpeechConfig'), \
             patch('azure.cognitiveservices.speech.SpeechRecognizer') as mock_recognizer_class, \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file:
            
            # Setup mocks
            mock_recognizer = Mock()
            mock_recognizer_class.return_value = mock_recognizer
            
            # Mock recognition error
            mock_result = Mock()
            mock_result.reason = Mock()
            mock_result.reason.name = "Canceled"
            mock_recognizer.recognize_once.return_value = mock_result
            
            mock_temp_file_obj = Mock()
            mock_temp_file_obj.name = "/tmp/test_audio.wav"
            mock_temp_file_obj.write = Mock()
            mock_temp_file_obj.flush = Mock()
            mock_temp_file.return_value.__enter__.return_value = mock_temp_file_obj
            mock_temp_file.return_value.__exit__.return_value = None
            
            with pytest.raises(SpeechRecognitionFailedError):
                await speech_service_configured.speech_to_text(mock_upload_file)
    
    def test_convert_to_wav_decode_error(self, speech_service_configured):
        """Test audio conversion with decode error."""
        with patch('pydub.AudioSegment.from_file') as mock_from_file:
            from pydub.exceptions import CouldntDecodeError
            mock_from_file.side_effect = CouldntDecodeError("Cannot decode file")
            
            with pytest.raises(InvalidAudioFileError) as exc_info:
                speech_service_configured._convert_to_wav("/tmp/input.webm", "/tmp/output.wav")
            
            assert "File must be a valid audio file" in str(exc_info.value)
    
    def test_convert_to_wav_ffmpeg_missing(self, speech_service_configured):
        """Test audio conversion when ffmpeg is missing."""
        with patch('pydub.AudioSegment.from_file') as mock_from_file:
            mock_from_file.side_effect = FileNotFoundError("ffprobe not found")
            
            with pytest.raises(SpeechRecognitionFailedError) as exc_info:
                speech_service_configured._convert_to_wav("/tmp/input.webm", "/tmp/output.wav")
            
            assert "Speech recognition service failed to process the audio" in str(exc_info.value)
    
    def test_convert_to_wav_file_not_found(self, speech_service_configured):
        """Test audio conversion with file not found."""
        with patch('pydub.AudioSegment.from_file') as mock_from_file:
            mock_from_file.side_effect = FileNotFoundError("Input file not found")
            
            with pytest.raises(SpeechRecognitionFailedError) as exc_info:
                speech_service_configured._convert_to_wav("/tmp/input.webm", "/tmp/output.wav")
            
            # The error message should contain information about the file not found
            assert "file" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()
    
    # ===== EDGE CASES =====
    
    @pytest.mark.asyncio
    async def test_speech_to_text_empty_audio_file(self, speech_service_configured):
        """Test speech to text with empty audio file."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "empty.wav"
        mock_file.content_type = "audio/wav"
        mock_file.read = AsyncMock(return_value=b"")
        
        # This should raise InvalidAudioFileError for empty file
        with pytest.raises(InvalidAudioFileError) as exc_info:
            await speech_service_configured.speech_to_text(mock_file)
        
        # Check that the error message contains information about empty or file validation
        assert any(word in str(exc_info.value).lower() for word in ["empty", "file", "invalid", "valid"])
    
    @pytest.mark.asyncio
    async def test_speech_to_text_large_file(self, speech_service_configured):
        """Test speech to text with large audio file."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "large_audio.wav"
        mock_file.content_type = "audio/wav"
        # Simulate a large file (1MB of data)
        mock_file.read = AsyncMock(return_value=b"x" * (1024 * 1024))
        
        with patch('azure.cognitiveservices.speech.SpeechConfig') as mock_speech_config, \
             patch('azure.cognitiveservices.speech.SpeechRecognizer') as mock_recognizer_class, \
             patch('azure.cognitiveservices.speech.audio.AudioConfig') as mock_audio_config, \
             patch('tempfile.NamedTemporaryFile') as mock_temp_file, \
             patch('builtins.open', mock_open()) as mock_file_open:
            
            # Setup mocks for successful processing
            mock_config = Mock()
            mock_speech_config.return_value = mock_config
            
            mock_recognizer = Mock()
            mock_recognizer_class.return_value = mock_recognizer
            
            mock_result = Mock()
            mock_result.text = "This is a long transcription from a large audio file"
            mock_result.reason = speechsdk.ResultReason.RecognizedSpeech
            mock_result.confidence = 0.85  # Set confidence as a float
            mock_recognizer.recognize_once.return_value = mock_result
            
            # Mock temp file context manager properly
            mock_temp_file_obj = Mock()
            mock_temp_file_obj.name = "/tmp/large_audio.wav"
            mock_temp_file_obj.write = Mock()
            mock_temp_file_obj.flush = Mock()
            mock_temp_file.return_value.__enter__.return_value = mock_temp_file_obj
            mock_temp_file.return_value.__exit__.return_value = None
            
            # Mock audio config
            mock_audio_config.return_value = Mock()
            
            # Execute
            result_text, confidence = await speech_service_configured.speech_to_text(mock_file)
            
            # Verify
            assert result_text == "This is a long transcription from a large audio file"
            assert confidence > 0.0
    
    def test_initialization_with_env_vars(self):
        """Test service initialization with different environment variable combinations."""
        # Test with all variables set
        with patch.dict(os.environ, {
            'AZURE_SPEECH_KEY': 'test_key',
            'AZURE_SPEECH_REGION': 'westus',
            'AZURE_SPEECH_ENDPOINT': 'https://test.cognitiveservices.azure.com/'
        }):
            service = AzureSpeechService()
            assert service.speech_key == 'test_key'
            assert service.speech_region == 'westus'
            assert service.speech_endpoint == 'https://test.cognitiveservices.azure.com/'
        
        # Test with minimal variables
        with patch.dict(os.environ, {
            'AZURE_SPEECH_KEY': 'test_key'
        }, clear=True):
            service = AzureSpeechService()
            assert service.speech_key == 'test_key'
            assert service.speech_region == 'eastus'  # default
            assert service.speech_endpoint is None
