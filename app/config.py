"""
Application configuration loaded from environment variables.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Each attribute here corresponds to a variable in .env file.
    """
    
    # API Keys - REQUIRED
    recall_api_key: str
    deepgram_api_key: str
    openai_api_key: str
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"
    log_level: str = "INFO"
    
    # WebSocket Configuration
    websocket_domain: str
    
    # CORS Origins - comma-separated string
    cors_origins: str = "http://localhost:3000"
    
    # Computed properties
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def redis_url(self) -> str:
        """Build Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        return f"redis://{self.redis_host}:{self.redis_port}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app_env.lower() == "production"
    
    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    @lru_cache() ensures we only load .env once.
    """
    return Settings()


if __name__ == "__main__":
    """Test configuration loading"""
    settings = get_settings()
    print("Configuration loaded successfully!")
    print(f"Environment: {settings.app_env}")
    print(f"Redis URL: {settings.redis_url}")
    print(f"CORS Origins: {settings.cors_origins_list}")
