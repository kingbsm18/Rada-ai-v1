from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://rada:rada@localhost:5432/rada_db"
    JWT_SECRET: str = "change_me_super_secret"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # paths (relative to backend/ by default)
    MEDIA_DIR: str = "../media"
    SNAPSHOTS_DIR: str = "../media/snapshots"
    CLIPS_DIR: str = "../media/clips"
    RECORDINGS_DIR: str = "../media/recordings"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
