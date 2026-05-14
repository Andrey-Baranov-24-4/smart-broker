from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://smart_broker:smart_broker@localhost:5432/smart_broker"
    commission_rate: float = 0.003
    cors_origins: str = "*"
    moex_base_url: str = "https://iss.moex.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
