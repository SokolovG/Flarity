# Flarity - Universal AI Log Analyzer

**Pluggable architecture** for intelligent log analysis that works with ANY infrastructure. Built with Clean Architecture principles - no vendor lock-in, easy to extend.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Flarity?

**Stop drowning in logs!** Flarity automatically:
- **Fetches** errors from your log system
- **Analyzes** with AI to explain what went wrong
- **Groups** similar issues to reduce noise
- **Delivers** smart reports via Telegram bot
- **Adapts** to YOUR infrastructure (not the other way around)


## Features

### Core Capabilities
- **AI Analysis**: Intelligent error analysis using LLM providers
- **AI Chat**: Interactive Q&A about errors you don't understand
- **Real-time Monitoring**: Fetches logs from any source in real-time
- **Telegram Bot**: Interactive bot for on-demand analysis
- **Statistics**: Error grouping, trending, and insights
- **Recent Errors**: Quick view of latest issues

### Architecture Benefits
- **Pluggable Design**: Swap providers without changing business logic
- **Clean Architecture**: Domain-driven design with clear boundaries
- **No Vendor Lock-in**: Use any log source, LLM, or notification service
- **Production Ready**: Redis caching, rate limiting, error handling

## Supported Integrations

### Log Sources
- ✅ **Loki** (built-in)
- 🔧 **Your custom source** (implement `LogSource` port)

### LLM Providers
- ✅ **Yandex GPT** (built-in)
- ✅ **Ollama** (built-in - local models)
- 🔧 **Your custom LLM** (implement `LLMAnalyzer` port)

### Notifications
- ✅ **Telegram** (built-in)
- 🔧 **Your custom notifier** (implement `Notifier` port)

### Storage
- ✅ **Redis** (built-in)
- ✅ **In-Memory** (built-in)

## Quick Start

### Prerequisites

- Python 3.12+
- Running Loki instance
- Telegram Bot Token
- LLM Provider (Yandex GPT API key OR use Ollama local)

### Installation
1. **Clone repository**
```bash
git clone https://github.com/SokolovG/flarity.git
cd flarity
```

2. **Install dependencies**
```bash
# Using uv (recommended)
pip install uv
uv sync
```

3. **Configure282138506ironment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run with Docker**
```bash
docker compose up --build
```

5. **Choose and pull ollama model (Optional)**
Choose model from list here: https://ollama.com/search
```bash
# Via docker compose
docker compose exec ollama ollama pull <model>

# Via Make file
make pull_model model=<model>
```


## Configuration
### Required Environment Variables
```env
# Log Source
LOG_SOURCE_PROVIDER=loki
LOG_SOURCE_CONFIG__URL=http://localhost:3100
LOG_SOURCE_CONFIG__APP_NAME=your-app-name

# LLM Provider (choose one)
LLM_PROVIDER_PROVIDER=yandex  # or ollama
LLM_MODEL=yandexgpt-lite  # or deepseek-r1:7b

# Yandex GPT (if using)
LLM_PROVIDER_CONFIG__API_KEY=your-api-key
LLM_PROVIDER_CONFIG__CATALOG_ID=your-folder-id

# Ollama (if using)
LLM_PROVIDER_CONFIG__BASE_URL=http://localhost:11434

# Telegram
NOTIFICATION_PROVIDER=telegram
NOTIFICATION_CONFIG__BOT_TOKEN=your-bot-token
NOTIFICATION_CONFIG__CHAT_ID=your-chat-id
(Optional)
NOTIFICATION_CONFIG__CHAT_ID_FOR_BUG_REPORT=your_chat_id_for_get_app_bugs_from_user

# Storage (optional)
STORAGE_PROVIDER=redis  # or memory
STORAGE_CONFIG__HOST=localhost
STORAGE_CONFIG__PORT=6379

# Scheduler (optional)
SCHEDULE_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6
```

### Customizing Prompts
If you want to change a basic prompt, edit /prompts/base_prompt.txt or create your own file.
```bash
cd resources/prompts
touch my_prompt.txt
#/src/infrastructure/settings/llm_settings.py
BASE_PROMPT_FILE_NAME = "my_prompt.txt"
```

### Templates
You can override default templates via environment variables:
```bash
# .env
REPORT_ANALYZE_TEMPLATE=my_custom_analysis.html
REPORT_RECENT_TEMPLATE=my_custom_template
# Don't forget to put your custom templates in resources/templates
```

## Telegram Bot Commands
```bash
/start - Get started
/help - List of commands
/analyze [hours] - AI analysis of logs (e.g., /analyze 6)
/recent [hours] - Recent errors without AI
/stats [hours] - Statistics summary
/settings - Current app settings
```
## Architecture
```
flarity/
├── src/
│   ├── domain/              # Business logic & entities
│   ├── application/         # Use cases & DTOs
│   ├── infrastructure/      # External integrations
│   │   ├── clients/        # HTTP clients (Loki, Telegram)
│   │   ├── llm/           # LLM provider adapters
│   │   ├── storage/       # Redis/Memory storage
│   │   └── settings/      # Configuration
│   └── interfaces/         # UI layer (Telegram bot)
├── resources/
│   ├── logs-example.log  # Example of a logs structure
│   ├── prompts/           # LLM prompts
│   └── templates/         # Report templates
│
│
└── tests/
```
## Development

### Setup

```bash
# Install dev dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run linting
uv run ruff check --fix
uv run ty check src/
```


### Adding a new group strategy (custom log format parsing)
```python
# 1. Create custom strategy
class MyCustomStrategy(ErrorGroupingStrategy):
    def extract_error_type(self, log: LogEntry) -> str:
        if "database" in log.message.lower():
            return "DATABASE_ERROR"
        elif "timeout" in log.message.lower():
            return "TIMEOUT_ERROR"
        return "UNKNOWN"

# 2. register in dependecncies
@provide(scope=Scope.APP)
    def get_error_grouper(self) -> ErrorGrouper:
        grouper = ErrorGrouper(strategy=MyCustomStrategy())
        return grouper
```

### Adding a new LLM Provider
```python
# 1. Create adapter in src/infrastructure/llm/
class NewAnalyzer(BaseLLMAnalyzer):
        # Your implementation all abstract methods

# 2. Add your provider and model to Enum
class LLMProvider(Enum):
    ...
    NEW_PROVIDER = "new_provider"

class LLMModel(str, Enum):
  ...
  CUSTOM_MODEL = "custom_model"

    @property
    def provider(self) -> LLMProvider:
        _PROVIDERS = {
            ...
            "custom_model": LLMProvider.<MODELS_PROVIDER>,
        }

# 3. Register in DI container
@provide(scope=Scope.APP)
def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> LLMAnalyzer:
    provider = LLMProvider(settings.llm_provider.provider)
    match provider:
        ...
        case LLMProvider.NEW_PROVIDER:
            return NewProvider(http_client, settings)

# 3. Add settings
class NewProviderSettings(BaseModel):
    api_key: str
    base_url: str
    # Custom fields...

# 4. Change .env
LLM_PROVIDER_PROVIDER=new_provider
LLM_MODEL=your_model
# ...other custom settings(API key, etc.)
