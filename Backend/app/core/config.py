from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agri-Care"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/agricare"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
