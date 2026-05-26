from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql://auditasec:auditasec_secret@localhost:5432/auditasecifc"
    session_secret_key: str = "dev-secret-key-change-me"
    admin_login: str = "admin"
    admin_password: str = "admin1"


settings = Settings()
