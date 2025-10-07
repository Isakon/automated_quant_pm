from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import yaml
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    alpha_vantage_api_key: Optional[str] = Field(None,alias="ALPHA_VANTAGE_API_KEY")
    twelve_data_api_key: Optional[str] = Field(None,alias="TWELVE_DATA_API_KEY")
    polygon_api_key: Optional[str] = Field(None,alias="POLYGON_API_KEY")
    finnhub_api_key: Optional[str] = Field(None,alias="FINNHUB_API_KEY")
    iex_cloud_api_key: Optional[str] = Field(None,alias="IEX_CLOUD_API_KEY")

    # Database
    database_url: str = Field("sqlite+aiosqlite:///./data/trading.db",alias="DATABASE_URL")

    # Redis
    redis_host: str = Field("localhost",alias="REDIS_HOST")
    redis_port: int = Field(6379,alias="REDIS_PORT")
    redis_db: int = Field(0,alias="REDIS_DB")
    redis_password: Optional[str] = Field(None,alias="REDIS_PASSWORD")

    # Application
    app_name: str = Field("AutomatedQuantPM",alias="APP_NAME")
    app_version: str = Field("1.0.0",alias="APP_VERSION")
    debug: bool = Field(False,alias="DEBUG")
    log_level: str = Field("INFO",alias="LOG_LEVEL")

    # Security
    secret_key: str = Field("change-me-in-production",alias="SECRET_KEY")
    api_key: Optional[str] = Field(None,alias="API_KEY")

    # Server
    host: str = Field("0.0.0.0",alias="HOST")
    port: int = Field(8000,alias="PORT")
    workers: int = Field(4,alias="WORKERS")

    # Trading
    trading_enabled: bool = Field(False,alias="TRADING_ENABLED")
    paper_trading: bool = Field(True,alias="PAPER_TRADING")
    default_risk_per_trade: float = Field(0.02,alias="DEFAULT_RISK_PER_TRADE")

    # Data Update Intervals
    realtime_update_interval: int = Field(60,alias="REALTIME_UPDATE_INTERVAL")
    historical_update_interval: int = Field(3600,alias="HISTORICAL_UPDATE_INTERVAL")

    # Model
    model_checkpoint_dir: str = Field("./data/models",alias="MODEL_CHECKPOINT_DIR")
    use_gpu: bool = Field(False,alias="USE_GPU")

    # Backtesting
    initial_capital: float = Field(100000,alias="INITIAL_CAPITAL")
    commission: float = Field(0.001,alias="COMMISSION")

    class Config:
        env_file = "credentials/.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class ConfigManager:
    """Manages application configuration from multiple sources"""

    def __init__(self):
        self.settings = Settings()
        self.config_path = Path("config")
        self.yaml_config = self._load_yaml_config()
        self.instruments = self._load_instruments()

    def _load_yaml_config(self) -> dict:
        """Load YAML configuration"""
        config_file = self.config_path / "config.yaml"
        if config_file.exists():
            with open(config_file,'r') as f:
                return yaml.safe_load(f)
        return {}

    def _load_instruments(self) -> dict:
        """Load instruments configuration"""
        instruments_file = self.config_path / "instruments.yaml"
        if instruments_file.exists():
            with open(instruments_file,'r') as f:
                return yaml.safe_load(f)
        return {}

    def get_watchlist(self) -> list:
        """Get default watchlist of instruments"""
        return self.instruments.get('default_watchlist',[])

    def get_all_instruments(self) -> dict:
        """Get all configured instruments"""
        return self.instruments

    def get_data_providers(self) -> list:
        """Get enabled data providers"""
        providers = self.yaml_config.get('data',{}).get('providers',[])
        return [p for p in providers if p.get('enabled',False)]


# Singleton instance
config_manager = ConfigManager()
settings = config_manager.settings