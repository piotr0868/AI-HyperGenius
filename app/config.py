from dataclasses import dataclass, field
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    api_key: str = field(default="", repr=False)
    provider: str = "groq"
    model: str = "openai/gpt-oss-20b"
    min_interval: float = 0
    port: int = 8765
    max_model_calls: int = 12
    max_tool_calls: int = 40
    max_corrections: int = 3
    max_quota_retries: int = 0
    max_output_tokens: int = 4000
    max_total_tokens: int = 120000
    command_timeout: int = 35
    task_timeout: int = 1200
    input_rate: float | None = None
    output_rate: float | None = None
    max_cost: float | None = None
    sandbox_image: str = ""

    @property
    def credential_var(self):
        return 'GROQ_API_KEY' if self.provider == 'groq' else 'AI_PROVIDER_KEY'

    @property
    def api_host(self):
        return 'api.groq.com' if self.provider == 'groq' else 'api.openai.com'


def load_settings() -> Settings:
    load_dotenv(ROOT / ".env", override=False)
    provider = os.getenv('AI_PROVIDER', 'groq').strip().lower()
    if provider not in ('groq', 'openai'):
        raise ValueError('AI_PROVIDER: scegli groq oppure openai.')
    def number(name, default, low, high):
        value = int(os.getenv(name, str(default)))
        if not low <= value <= high:
            raise ValueError(f"{name}: usa un valore tra {low} e {high}.")
        return value
    def price(name):
        raw = os.getenv(name, "").strip()
        value = float(raw) if raw else None
        if value is not None and (value < 0 or not __import__('math').isfinite(value)):
            raise ValueError(f"{name}: prezzo non valido.")
        return value
    return Settings(
        data_dir=Path(os.getenv("APP_DATA_DIR", str(ROOT / ".data"))).resolve(),
        api_key=os.getenv('GROQ_API_KEY' if provider == 'groq' else 'AI_PROVIDER_KEY', ''),
        provider=provider,
        model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b') if provider == 'groq' else os.getenv('AI_MODEL', 'gpt-5-mini'),
        min_interval=number('AI_MIN_INTERVAL_SECONDS', 60 if provider == 'groq' else 0, 0, 60),
        port=number("APP_PORT", 8765, 1024, 65535),
        max_model_calls=number("MAX_MODEL_CALLS", 12, 1, 40),
        max_tool_calls=number("MAX_TOOL_CALLS", 40, 1, 100),
        max_corrections=number("MAX_CORRECTIONS", 3, 0, 5),
        max_quota_retries=number("MAX_RATE_LIMIT_RETRIES", 2 if provider == 'groq' else 0, 0, 2),
        max_output_tokens=number("MAX_OUTPUT_TOKENS", 4000, 500, 12000),
        max_total_tokens=number("MAX_TOTAL_TOKENS", 120000, 1000, 500000),
        command_timeout=number("COMMAND_TIMEOUT_SECONDS", 35, 5, 90),
        task_timeout=number("TASK_TIMEOUT_SECONDS", 1200, 30, 3600),
        input_rate=price("AI_INPUT_USD_PER_MILLION"),
        output_rate=price("AI_OUTPUT_USD_PER_MILLION"),
        max_cost=price("MAX_ESTIMATED_COST_USD"),
        sandbox_image=os.getenv("SANDBOX_IMAGE", ""),
    )
