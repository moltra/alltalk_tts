"""
Custom exception classes for AllTalk TTS application.

This module provides a hierarchy of custom exceptions for better error handling
and debugging throughout the application.
"""


class AllTalkError(Exception):
    """Base exception for AllTalk application"""

    pass


class ConfigurationError(AllTalkError):
    """Raised when configuration is invalid"""

    pass


class TTSEngineError(AllTalkError):
    """Raised when TTS engine fails"""

    pass


class ModelLoadError(TTSEngineError):
    """Raised when model fails to load"""

    pass


class AudioProcessingError(AllTalkError):
    """Raised when audio processing fails"""

    pass


class APIError(AllTalkError):
    """Raised when API request fails"""

    pass
