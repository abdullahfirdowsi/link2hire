"""
Utility functions and helpers for the Link2Hire application.
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime
import traceback


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("link2hire.log", mode="a")
        ]
    )
    
    # Set specific loggers
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("gspread").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format exception into error response dictionary.
    
    Args:
        error: Exception object
        
    Returns:
        Formatted error dictionary
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    return {
        "error": error_message,
        "error_type": error_type,
        "timestamp": datetime.utcnow().isoformat()
    }


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim whitespace
    text = text.strip()
    
    # Enforce max length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_traceback(error: Exception) -> str:
    """
    Extract full traceback from exception.
    
    Args:
        error: Exception object
        
    Returns:
        Formatted traceback string
    """
    return ''.join(traceback.format_exception(
        type(error),
        error,
        error.__traceback__
    ))


def validate_environment() -> Dict[str, bool]:
    """
    Validate that all required environment variables are set.
    
    Returns:
        Dictionary with validation results
    """
    from backend.config import settings
    
    validations = {
        "azure_openai": bool(settings.azure_openai_endpoint and settings.azure_openai_api_key),
        "mongodb": bool(settings.mongodb_connection_string),
        "google_sheets": bool(settings.google_sheets_credentials_path and settings.google_sheets_spreadsheet_id)
    }
    
    return validations


def get_health_status() -> Dict[str, Any]:
    """
    Get application health status.
    
    Returns:
        Health status dictionary
    """
    validations = validate_environment()
    
    return {
        "status": "healthy" if all(validations.values()) else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": validations,
        "version": "1.0.0"
    }


class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        """Initialize timing context."""
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        """Start timing."""
        self.start_time = datetime.utcnow()
        self.logger.debug(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration."""
        self.end_time = datetime.utcnow()
        self.duration = (self.end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                f"Completed: {self.operation_name} in {self.duration:.3f}s"
            )
        else:
            self.logger.error(
                f"Failed: {self.operation_name} after {self.duration:.3f}s - {exc_val}"
            )
        
        return False  # Don't suppress exceptions
