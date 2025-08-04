"""
Centralized logging configuration for the Flights Chatbot Assistant API.

This module provides structured logging with:
- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output
- Color-coded console output
- Proper separation of INFO/WARNING to stdout and ERROR to stderr
- JSON formatting for production use
"""

import logging
import logging.handlers
import sys
import os
from typing import Optional
from pathlib import Path
import colorlog
from pydantic import BaseModel, Field
from opencensus.ext.azure.log_exporter import AzureLogHandler 


class LoggingConfig(BaseModel):
    """Configuration for logging system."""
    log_level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Global log level (env: LOG_LEVEL)"
    )
    log_file: str = Field(
        default_factory=lambda: os.getenv("LOG_FILE", "logs/flights-chatbot.log"),
        description="Main log file path (env: LOG_FILE)"
    )
    error_log_file: str = Field(
        default_factory=lambda: os.getenv("ERROR_LOG_FILE", "logs/flights-chatbot-errors.log"),
        description="Error log file path (env: ERROR_LOG_FILE)"
    )
    max_file_size: int = Field(
        default_factory=lambda: int(os.getenv("MAX_LOG_FILE_SIZE", str(10 * 1024 * 1024))),
        description="Max log file size in bytes (env: MAX_LOG_FILE_SIZE, default: 10MB)"
    )
    backup_count: int = Field(default=5, description="Number of backup log files to keep")
    console_colors: bool = Field(default=True, description="Enable colored console output")
    json_format: bool = Field(
        default_factory=lambda: os.getenv("LOG_JSON_FORMAT", "false").lower() in ("true", "1", "yes"),
        description="Use JSON formatting for production (env: LOG_JSON_FORMAT)"
    )


class LoggingManager:
    """Manages logging configuration and provides loggers."""
    
    def __init__(self, config: Optional[LoggingConfig] = None) -> None:
        self.config: LoggingConfig = config or LoggingConfig()
        self._is_initialized: bool = False
        self.main_logger: Optional[logging.Logger] = None
    
    def initialize(self) -> None:
        """Initialize the logging system."""
        if self._is_initialized:
            return
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.config.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear any existing handlers
        logging.getLogger().handlers.clear()
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Create formatters
        if self.config.json_format:
            file_formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s", '
                '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
            )
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
            )
        
        # Console formatter with colors
        if self.config.console_colors:
            console_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # File handler for all logs (rotating)
        file_handler = logging.handlers.RotatingFileHandler(
            self.config.log_file,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # File handler for errors only (rotating)
        error_file_handler = logging.handlers.RotatingFileHandler(
            self.config.error_log_file,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(file_formatter)
        
        # Console handler for INFO and WARNING (stdout)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)
        stdout_handler.setFormatter(console_formatter)
        
        # Console handler for ERROR and CRITICAL (stderr)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        stderr_handler.setFormatter(console_formatter)
        
        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_file_handler)
        root_logger.addHandler(stdout_handler)
        root_logger.addHandler(stderr_handler)

        # NUEVO: Azure Application Insights handler
        app_insights_conn_str = os.getenv("APPINSIGHTS_CONNECTION_STRING")
        if app_insights_conn_str:
            azure_handler = AzureLogHandler(connection_string=app_insights_conn_str)
            azure_handler.setLevel(logging.INFO)
            root_logger.addHandler(azure_handler)
            root_logger.info("Azure Application Insights logging is enabled.")
        else:
            root_logger.warning("APPINSIGHTS_CONNECTION_STRING not set; skipping AzureLogHandler.")

        
        # Create main application logger
        self.main_logger = logging.getLogger("flights_chatbot")
        
        self._is_initialized = True
        self.main_logger.info("Logging system configured successfully")
        self.main_logger.info(f"Log level: {self.config.log_level}")
        self.main_logger.info(f"Main log file: {self.config.log_file}")
        self.main_logger.info(f"Error log file: {self.config.error_log_file}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        if not self._is_initialized:
            self.initialize()
        return logging.getLogger(f"flights_chatbot.{name}")
    
    def is_initialized(self) -> bool:
        """Check if the logging manager is initialized."""
        return self._is_initialized
    
    def check_critical_env_vars(self) -> None:
        """Check for critical environment variables and fail fast if missing."""
        logger = self.get_logger("startup")
        
        # Check for OPENAI_API_KEY
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            logger.critical("OPENAI_API_KEY environment variable is not set!")
            logger.critical("This is required for the LLM chat functionality to work.")
            logger.critical("Please set the OPENAI_API_KEY environment variable and restart the server.")
            raise SystemExit("FATAL: Missing required OPENAI_API_KEY environment variable")
        
        logger.info("✓ OPENAI_API_KEY environment variable is configured")
        
        # Check for SECRET_KEY (warning only)
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key or secret_key == "please_guys_do_not_forget_to_set_a_secret_key":
            logger.warning("SECRET_KEY environment variable is not set or using default value!")
            logger.warning("This is not secure for production. Please set a proper SECRET_KEY.")
        else:
            logger.info("✓ SECRET_KEY environment variable is configured")


# Global logging manager instance - Singleton pattern
logging_manager = LoggingManager()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger."""
    return logging_manager.get_logger(name)


def configure_logging(config: Optional[LoggingConfig] = None) -> None:
    """Configure the logging system with optional custom config."""
    global logging_manager
    if config:
        logging_manager = LoggingManager(config)
    logging_manager.initialize()


def check_critical_env_vars() -> None:
    """Check for critical environment variables and fail fast if missing."""
    logging_manager.check_critical_env_vars()
