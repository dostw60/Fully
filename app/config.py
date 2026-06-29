from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    live_provider_url: str = "https://nepseapi-production.up.railway.app/api"
    history_provider_url: str = "https://nepse-data-api.onrender.com/api"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()