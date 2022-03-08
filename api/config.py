from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE: int
    ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()
