"""Environment-based application settings."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    environment: str = "development"
    database_url: str = "sqlite:///./gati_shram.db"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:3000"
    privacy_epsilon: float = 1.0
    privacy_min_group_size: int = 1
    privacy_demo_noise_enabled: bool = False
    privacy_demo_noise_scale: float = 0.0
    privacy_demo_random_seed: int = 7
    gravity_alpha: float = 0.8
    gravity_gamma: float = 0.9
    gravity_beta: float = 1.2
    gravity_delta: float = 0.7
    gravity_epsilon: float = 1.0
    early_warning_low_threshold: float = 0.33
    early_warning_medium_threshold: float = 0.66
    forecast_window: int = 4
    data_mode: str = "demo"
    public_mobility_csv_path: str = "data/raw/mobility.csv"
    public_geography_csv_path: str = "data/raw/geography.csv"
    public_historical_csv_path: str = "data/raw/historical_observations.csv"
    public_data_fetch_enabled: bool = False
    public_request_timeout: int = 10
    onorc_api_url: str = ""
    onorc_api_key: str = ""
    railways_uts_api_url: str = ""
    railways_uts_api_key: str = ""
    eshram_api_url: str = ""
    eshram_api_key: str = ""


def get_settings() -> Settings:
    """Build settings without requiring secrets or external services."""
    return Settings(
        environment=os.getenv("ENVIRONMENT", "development"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./gati_shram.db"),
        api_version=os.getenv("API_VERSION", "1.0.0"),
        api_host=os.getenv("API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("API_PORT", "8000")),
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
        privacy_epsilon=float(os.getenv("PRIVACY_EPSILON", "1.0")),
        privacy_min_group_size=int(os.getenv("PRIVACY_MIN_GROUP_SIZE", "1")),
        privacy_demo_noise_enabled=os.getenv("PRIVACY_DEMO_NOISE_ENABLED", "false").lower() == "true",
        privacy_demo_noise_scale=float(os.getenv("PRIVACY_DEMO_NOISE_SCALE", "0.0")),
        privacy_demo_random_seed=int(os.getenv("PRIVACY_DEMO_RANDOM_SEED", "7")),
        gravity_alpha=float(os.getenv("GRAVITY_ALPHA", "0.8")),
        gravity_gamma=float(os.getenv("GRAVITY_GAMMA", "0.9")),
        gravity_beta=float(os.getenv("GRAVITY_BETA", "1.2")),
        gravity_delta=float(os.getenv("GRAVITY_DELTA", "0.7")),
        gravity_epsilon=float(os.getenv("GRAVITY_EPSILON", "1.0")),
        early_warning_low_threshold=float(os.getenv("EARLY_WARNING_LOW_THRESHOLD", "0.33")),
        early_warning_medium_threshold=float(os.getenv("EARLY_WARNING_MEDIUM_THRESHOLD", "0.66")),
        forecast_window=int(os.getenv("FORECAST_WINDOW", "4")),
        data_mode=os.getenv("DATA_MODE", "demo").lower(),
        public_mobility_csv_path=os.getenv("PUBLIC_MOBILITY_CSV_PATH", "data/raw/mobility.csv"),
        public_geography_csv_path=os.getenv("PUBLIC_GEOGRAPHY_CSV_PATH", "data/raw/geography.csv"),
        public_historical_csv_path=os.getenv("PUBLIC_HISTORICAL_CSV_PATH", "data/raw/historical_observations.csv"),
        public_data_fetch_enabled=os.getenv("PUBLIC_DATA_FETCH_ENABLED", "false").lower() == "true",
        public_request_timeout=int(os.getenv("PUBLIC_REQUEST_TIMEOUT", "10")),
        onorc_api_url=os.getenv("ONORC_API_URL", ""),
        onorc_api_key=os.getenv("ONORC_API_KEY", ""),
        railways_uts_api_url=os.getenv("RAILWAYS_UTS_API_URL", ""),
        railways_uts_api_key=os.getenv("RAILWAYS_UTS_API_KEY", ""),
        eshram_api_url=os.getenv("ESHRAM_API_URL", ""),
        eshram_api_key=os.getenv("ESHRAM_API_KEY", ""),
    )
