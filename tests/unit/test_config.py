"""
Unit tests for configuration module.
"""

import pytest
import os
from app.config import Settings


def test_settings_from_env(monkeypatch):
    """Test Settings loads from environment variables"""
    monkeypatch.setenv("RECALL_API_KEY", "test_recall_key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("WEBSOCKET_DOMAIN", "test.example.com")
    
    settings = Settings()
    
    assert settings.recall_api_key == "test_recall_key"
    assert settings.deepgram_api_key == "test_deepgram_key"
    assert settings.openai_api_key == "test_openai_key"
    assert settings.websocket_domain == "test.example.com"


def test_settings_defaults(monkeypatch):
    """Test Settings default values"""
    monkeypatch.setenv("RECALL_API_KEY", "test_recall_key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("WEBSOCKET_DOMAIN", "test.example.com")
    
    settings = Settings()
    
    assert settings.redis_host == "localhost"
    assert settings.redis_port == 6379
    assert settings.app_host == "0.0.0.0"
    assert settings.app_port == 8000
    assert settings.app_env == "development"


def test_redis_url_without_password(monkeypatch):
    """Test Redis URL generation without password"""
    monkeypatch.setenv("RECALL_API_KEY", "test_recall_key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("WEBSOCKET_DOMAIN", "test.example.com")
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    
    settings = Settings()
    
    assert settings.redis_url == "redis://localhost:6379"


def test_redis_url_with_password(monkeypatch):
    """Test Redis URL generation with password"""
    monkeypatch.setenv("RECALL_API_KEY", "test_recall_key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("WEBSOCKET_DOMAIN", "test.example.com")
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_PASSWORD", "secret")
    
    settings = Settings()
    
    assert settings.redis_url == "redis://:secret@localhost:6379"


def test_cors_origins_list(monkeypatch):
    """Test CORS origins parsing"""
    monkeypatch.setenv("RECALL_API_KEY", "test_recall_key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("WEBSOCKET_DOMAIN", "test.example.com")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    
    settings = Settings()
    
    assert settings.cors_origins_list == ["http://localhost:3000", "http://localhost:8000"]


def test_is_production(monkeypatch):
    """Test production environment detection"""
    monkeypatch.setenv("RECALL_API_KEY", "test_recall_key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("WEBSOCKET_DOMAIN", "test.example.com")
    monkeypatch.setenv("APP_ENV", "production")
    
    settings = Settings()
    
    assert settings.is_production is True


def test_is_not_production(monkeypatch):
    """Test non-production environment detection"""
    monkeypatch.setenv("RECALL_API_KEY", "test_recall_key")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "test_deepgram_key")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("WEBSOCKET_DOMAIN", "test.example.com")
    monkeypatch.setenv("APP_ENV", "development")
    
    settings = Settings()
    
    assert settings.is_production is False
