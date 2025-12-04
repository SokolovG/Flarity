# Flarity

AI-powered log analyzer that automatically fetches error logs from Log Source, analyzes them using LLM providers, and sends intelligent digest reports to Telegram.

## Quick Start

### Prerequisites

- Python 3.12+
- Running Loki instance (for log aggregation)
- Telegram Bot Token
- LLM Provider:
  - **YandexGPT** API Key
  - **Ollama** local, free

### Installation


1. Install dependencies:
```bash
uv sync
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Configure environment variables (see Configuration section)

4. Run the service:
```bash
docker build -t <image-name> .
docker run --env-file .env <image-name>
```

## Configuration

Create a `.env` file in the project root:

```env
# Loki Configuration
LOKI_URL=http://localhost:3100
LOKI_APP_NAME=your-app-name

# LLM
LLM_PROVIDER_PROVIDER=yandex OR ollama
LLM_MODEL=deepseek-r1:latest OR yandex-gpt-lite OR ...
LLM_TEMPERATURE=0.6
LLM_MAX_TOKENS=1000

# YandexGPT (if using)
LLM_PROVIDER_YANDEX_CATALOG_ID=your-folder-id
LLM_PROVIDER_YANDEX_API_KEY=your-api-key
LLM_PROVIDER_YANDEX_BASE_URL=https://llm.api.cloud.yandex.net/foundationModels/v1/completion

# Ollama (if using)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Analysis Settings
SCHEDULE_INTERVAL_HOURS=24
```

**Key Components:**
- `HTTPClient` - Shared HTTP client with retry logic
- `LokiClient` - Loki API integration
- `LLMService` - Abstract LLM provider interface
- `YandexAdapter` / `OllamaAdapter` - Provider-specific implementations
- `TelegramClient` - Telegram Bot API client
- `LogAnalysisService` - Orchestrates the analysis workflow

**Prompt:**
If you want to change a basic prompt, edit /prompts/base_prompt.txt


## Development

### Setup

1. Install and run pre commit
```bash
uv add pre-commit
pre-commit install
```

### Testing

```bash
# Send fake logs to Loki (for testing)
python tests/send_logs_to_loki.py
```

## Architecture

Flarity follows **clean architecture** principles with strict separation of concerns and dependency inversion.

### High-Level Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (Entry Point)                    │
│                  Orchestrates workflow                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Dishka DI Container (core/container.py)        │
│           Manages all dependencies & lifetimes              │
└───────┬──────────────────┬──────────────────┬───────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────────────┐
│   Services    │  │   Clients    │  │    LLM Adapters      │
│ (Business     │  │ (External    │  │  (Provider-specific) │
│  Logic)       │  │  APIs)       │  │                      │
│               │  │              │  │                      │
│ - LogAnalysis │  │ - Loki       │  │ - YandexAdapter      │
│ - ReportFormat│  │ - Telegram   │  │ - OllamaAdapter      │
└───────────────┘  └──────┬───────┘  └──────┬───────────────┘
                          │                  │
                          ▼                  ▼
                  ┌────────────────────────────────┐
                  │   HTTPClient (shared base)     │
                  │  - Retry logic                 │
                  │  - Error mapping               │
                  │  - Logging                     │
                  └────────────────────────────────┘
```


```
flarity/
├── prompts/
│   ├── base_prompt.txt  # Basic prompt for llm
├── src/
│   ├── main.py          # Entry point
│   ├── llm_adapters/    # LLM provider adapters
│   ├── clients/         # HTTP clients (Loki, Telegram, CustomHttp)
│   ├── core/            # Settings, DI container, decorators
│   ├── entities/        # Domain models
│   ├── exceptions/      # Custom exceptions
│   ├── responses/       # API response models
│   └── services/        # Business logic
├── tests/
├── .env.example
├── uv.lock
└── Dockerfile
```

### Adding a New LLM Provider
```python
# 1. Create adapter in llm_adapters/
class NewProviderAdapter(LLMService):
    async def analyze_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        # Your implementation
        ...

# 2. Add your provider and model to Enum
class LLMProvider(Enum):
  ...
  NEW_PROVIDER = "new_provider"

class LLMModel(Enum):
  ...
  MODEL = "model"

# 3. Register in DI container
def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> BaseLLMAdapter:
  provider = LLMProvider(settings.llm_provider.provider)
  case LLMProvider.OLLAMA:
      return OllamaAdapter(http_client, settings)
    # ...

# 3. Add settings
class NewProviderSettings(BaseModel):
    api_key: str
    base_url: str

# 4. Change .env
LLM_PROVIDER_PROVIDER=new_provider
LLM_MODEL=your_model
```

## Local LLM

1. Install ollama
```bash
#MACOS
brew install ollama
#Linux
curl -fsSL https://ollama.com/install.sh | sh
#Windows
https://ollama.com/download/windows
```

2. Run ollama
```bash
# start ollama server in foreground
ollama serve
# start ollama server in background
ollama serve &

# if ollama installed using Homebrew
brew services start ollama
```

3. Adding new local model

```bash
# Choose model from list here: https://ollama.com/search
ollama pull deepseek-r1:7b
```

4. See installed models

```bash
ollama list
```

5. Expose local llm for api
Ollama exposes a HTTP API at localhost:11434.
Add url to .env
