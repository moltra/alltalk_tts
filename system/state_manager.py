"""
Centralized state management for AllTalk TTS application.

This module provides a StateManager class to manage global application state
instead of using global variables, improving testability and thread safety.
"""
from typing import Optional
from asyncio import Lock

from config import AlltalkConfig, AlltalkTTSEnginesConfig


class StateManager:
    """Centralized state management for AllTalk application"""
    
    def __init__(self):
        self._config: Optional[AlltalkConfig] = None
        self._tts_engines_config: Optional[AlltalkTTSEnginesConfig] = None
        self._infer_pipeline = None
        self._lock = Lock()
    
    @property
    def config(self) -> AlltalkConfig:
        """Get the current AlltalkConfig instance"""
        if self._config is None:
            self._config = AlltalkConfig.get_instance()
        return self._config
    
    @property
    def tts_engines_config(self) -> AlltalkTTSEnginesConfig:
        """Get the current AlltalkTTSEnginesConfig instance"""
        if self._tts_engines_config is None:
            self._tts_engines_config = AlltalkTTSEnginesConfig.get_instance()
        return self._tts_engines_config
    
    @property
    def infer_pipeline(self):
        """Get the current infer_pipeline instance"""
        return self._infer_pipeline
    
    @infer_pipeline.setter
    def infer_pipeline(self, value):
        """Set the infer_pipeline instance"""
        self._infer_pipeline = value
    
    async def reload_config(self, force: bool = False):
        """Reload configuration instances"""
        async with self._lock:
            self._config = AlltalkConfig.get_instance(force_reload=force)
            self._tts_engines_config = AlltalkTTSEnginesConfig.get_instance(force_reload=force)
    
    async def initialize_infer_pipeline(self):
        """Initialize the infer_pipeline based on RVC settings"""
        async with self._lock:
            if self.config.rvc_settings.rvc_enabled:
                from system.tts_engines.rvc.infer.infer import infer_pipeline as rvc_pipeline
                self._infer_pipeline = rvc_pipeline
            else:
                self._infer_pipeline = None
    
    def reset(self):
        """Reset all state (useful for testing)"""
        self._config = None
        self._tts_engines_config = None
        self._infer_pipeline = None


# Global state manager instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get the global StateManager instance (singleton pattern)"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def reset_state_manager():
    """Reset the global StateManager instance (useful for testing)"""
    global _state_manager
    _state_manager = None
