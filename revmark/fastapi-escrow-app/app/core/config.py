from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    DATABASE_NAME: str

    # Stripe settings
    STRIPE_API_KEY: str
    STRIPE_CONNECT_CLIENT_ID: str

    # Other settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()