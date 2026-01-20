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

**Required:**
- Python 3.12+
- Running Loki instance (for log collection)
- Telegram Bot Token ([create bot](https://t.me/BotFather))
- LLM Provider:
  - Yandex GPT API key, OR
  - Ollama (local, free)

**Optional:**
- Redis 6.0+ (for persistent storage, recommended for production)

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

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run application**

**Development:**
```bash
docker compose up --build
```

**Production:**
```bash
# First, remove volumes from docker-compose.yml or create docker-compose.prod.yml
docker compose up -d --build
```

⚠️ **Important for production**: Remove `volumes: - .:/app` from `docker-compose.yml` to use the code baked into the Docker image, not the host filesystem.

5. **Pull Ollama model** (if using Ollama)

Choose model from: https://ollama.com/search
```bash
# Via docker compose
docker compose exec ollama ollama pull deepseek-r1:7b

# Via Makefile
make pull_model model=deepseek-r1:7b
```

## Configuration

### Required Environment Variables

```env
# === Log Source ===
LOG_SOURCE_PROVIDER=loki
LOG_SOURCE_CONFIG__URL=http://localhost:3100
LOG_SOURCE_CONFIG__APP_NAME=your-app-name

# === LLM Provider === (choose one)
LLM_PROVIDER_PROVIDER=yandex  # or ollama
LLM_MODEL=yandexgpt-lite  # or deepseek-r1:7b

# Yandex GPT (if using)
LLM_PROVIDER_CONFIG__API_KEY=your-api-key
LLM_PROVIDER_CONFIG__CATALOG_ID=your-folder-id

# Ollama (if using)
LLM_PROVIDER_CONFIG__BASE_URL=http://localhost:11434

# === Telegram ===
NOTIFICATION_PROVIDER=telegram
NOTIFICATION_CONFIG__BOT_TOKEN=your-bot-token
NOTIFICATION_CONFIG__CHAT_ID=your-chat-id

# === Storage === (optional, default: memory)
STORAGE_PROVIDER=redis  # or memory

# Redis configuration (required if STORAGE_PROVIDER=redis)
STORAGE_CONFIG__HOST=localhost
STORAGE_CONFIG__PORT=6379
STORAGE_CONFIG__DB=0
STORAGE_CONFIG__PASSWORD=your-strong-password  # CHANGE THIS!

# === Scheduler === (optional)
SCHEDULE_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6
```

### Bug Reports Configuration

Users can report bugs via `/bug` command. Configure where reports are sent:

```env
# Chat ID where bug reports will be sent (get from @userinfobot)
NOTIFICATION_CONFIG__CHAT_ID_FOR_BUG_REPORT=your_admin_chat_id
```

### Customizing Prompts

Create your custom prompt file:
```bash
cd resources/prompts
touch my_prompt.txt
# Edit my_prompt.txt with your custom prompt
```

Update the prompt filename in `src/infrastructure/settings/providers.py`:
```python
# Change this line:
BASE_PROMPT_FILE_NAME = "my_prompt.txt"  # Default: "base_prompt.txt"
```

### Templates

You can override default templates via environment variables:
```env
# .env
REPORT_ANALYZE_TEMPLATE=my_custom_analysis.html
REPORT_RECENT_TEMPLATE=my_custom_recent.html
REPORT_STATS_TEMPLATE=my_custom_stats.html
# Don't forget to put your custom templates in resources/templates
```

## Telegram Bot Commands

```
/start - Get started
/help - List of commands
/analyze [hours] - AI analysis of logs (e.g., /analyze 6)
/recent [hours] - Recent errors without AI
/stats [hours] - Statistics summary
/settings - Current app settings
/bug - Report a bug
/menu - Return to main menu
```

## Architecture

### Project Structure

```
flarity/
├── src/
│   ├── domain/                    # Core business logic (no dependencies)
│   │   ├── entities/             # Domain models (LogEntry, Enums)
│   │   ├── services/             # Domain services (ErrorGrouper)
│   │   ├── value_objects/        # Value objects (TimeRange)
│   │   └── exceptions.py         # Domain exceptions
│   │
│   ├── application/               # Use cases (orchestration)
│   │   ├── use_cases/            # Business workflows
│   │   ├── dto/                  # Data transfer objects
│   │   └── ports/                # Interfaces for infrastructure
│   │
│   ├── infrastructure/            # External integrations
│   │   ├── clients/              # HTTP clients (Loki, Telegram)
│   │   ├── llm/                  # LLM provider adapters
│   │   │   ├── yandex/          # Yandex GPT adapter
│   │   │   └── ollama/          # Ollama adapter
│   │   ├── storage/              # Storage implementations
│   │   │   ├── redis_storage.py
│   │   │   └── in_memory_storage.py
│   │   ├── repositories/         # Data access layer
│   │   ├── settings/             # Configuration management
│   │   └── di/                   # Dependency injection
│   │
│   └── interfaces/                # Entry points
│       ├── bot/                  # Telegram bot UI
│       │   ├── dialogs/         # aiogram-dialog windows
│       │   ├── handlers/        # Command handlers
│       │   └── formatters/      # Report formatting
│       └── scheduler/            # Background tasks
│
├── resources/
│   ├── prompts/                  # LLM system prompts
│   └── templates/                # Jinja2 report templates
│
└── tests/                        # Tests (TODO)
```

### Clean Architecture Layers

- **Domain**: Business rules, no external dependencies
- **Application**: Use cases, depends only on Domain
- **Infrastructure**: External services, implements Application ports
- **Interfaces**: User-facing entry points (bot, scheduler)

**Dependency Rule**: Inner layers never depend on outer layers.

## Development

### Setup

```bash
# Install dev dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Run type checking
uv run ty check src/

# Run linting
uv run ruff check --fix
uv run ruff format

# Tests (TODO: not implemented yet)
# uv run pytest
```

### Adding a New Error Grouping Strategy

```python
# 1. Create strategy in src/domain/services/error_grouper.py
class MyCustomStrategy(ErrorGroupingStrategy):
    def extract_error_type(self, log: LogEntry) -> str:
        if "database" in log.message.lower():
            return "DATABASE_ERROR"
        elif "timeout" in log.message.lower():
            return "TIMEOUT_ERROR"
        return "UNKNOWN"

# 2. Update src/infrastructure/di/dependencies.py
@provide(scope=Scope.APP)
def get_error_grouper(self) -> ErrorGrouper:
    return ErrorGrouper(strategy=MyCustomStrategy())
```

### Adding a New LLM Provider

```python
# 1. Add provider to LLMProvider enum (src/domain/entities/enums.py)
class LLMProvider(Enum):
    OLLAMA = "ollama"
    YANDEX = "yandex"
    OPENAI = "openai"  # ← New provider

# 2. Add models to LLMModel enum
class LLMModel(str, Enum):
    # ... existing models
    GPT_4 = "gpt-4"
    GPT_3_5 = "gpt-3.5-turbo"

    @property
    def provider(self) -> LLMProvider:
        _PROVIDERS = {
            # ... existing mappings
            "gpt-4": LLMProvider.OPENAI,
            "gpt-3.5-turbo": LLMProvider.OPENAI,
        }
        provider = _PROVIDERS.get(self.value)
        if provider is None:
            raise ValueError(f"Model '{self.value}' is not mapped to any provider")
        return provider

# 3. Create adapter in src/infrastructure/llm/openai/analyzer.py
class OpenAIAnalyzer(BaseLLMAnalyzer):
    def __init__(self, http_client: HTTPClient, settings: AppSettings) -> None:
        super().__init__(http_client, settings)

    def _get_api_url(self) -> str:
        return "https://api.openai.com/v1/chat/completions"

    def _get_headers(self) -> dict[str, Any]:
        return {
            "Authorization": f"Bearer {self.settings.llm_provider.get_config(OpenAIConfig).api_key}",
            "Content-Type": "application/json",
        }

    def _build_request(self, logs_text: str) -> tuple[dict[str, Any], list[LLMMessage]]:
        messages = [
            LLMMessage(role="system", text=self.settings.llm_settings.system_prompt),
            LLMMessage(role="user", text=logs_text),
        ]
        request_data = {
            "model": self.settings.llm_settings.model.value,
            "messages": [{"role": m.role, "content": m.text} for m in messages],
            "max_tokens": self.settings.llm_settings.max_tokens,
        }
        return request_data, messages

    # Implement other abstract methods...

# 4. Add settings (src/infrastructure/settings/providers.py)
class OpenAIConfig(BaseLLMProviderConfig):
    api_key: str
    base_url: str = "https://api.openai.com/v1/chat/completions"

# 5. Update LLMProviderSettings.get_config() to handle OpenAIConfig

# 6. Register in DI (src/infrastructure/di/dependencies.py)
@provide(scope=Scope.APP)
def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> LLMAnalyzer:
    provider = LLMProvider(settings.llm_provider.provider)
    match provider:
        case LLMProvider.YANDEX:
            return YandexAnalyzer(http_client, settings)
        case LLMProvider.OLLAMA:
            return OllamaAnalyzer(http_client, settings)
        case LLMProvider.OPENAI:
            return OpenAIAnalyzer(http_client, settings)

# 7. Update .env
LLM_PROVIDER_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_PROVIDER_CONFIG__API_KEY=sk-your-key-here
```

### Adding a New Log Source

```python
# 1. Create client in src/infrastructure/clients/your_source_client.py
class YourSourceClient:
    async def query_logs(self, start: datetime, end: datetime) -> YourResponse:
        # Implementation

# 2. Create repository in src/infrastructure/repositories/your_source/
class YourSourceRepository(LogSource):
    async def get_errors(self, time_range: TimeRange) -> list[LogEntry]:
        # Implementation

    async def check_readiness(self) -> bool:
        # Implementation

# 3. Register in DI (src/infrastructure/di/dependencies.py)
@provide(scope=Scope.APP)
def get_log_source(self, your_client: YourSourceClient) -> LogSource:
    return YourSourceRepository(your_client)
```

## Troubleshooting

### "Ollama model not found"

**Error:** `Ollama model not found. Did you run 'ollama pull'?`

**Solution:**
```bash
# Pull the model
docker compose exec ollama ollama pull deepseek-r1:7b

# Or use Makefile
make pull_model model=deepseek-r1:7b

# Verify model is available
docker compose exec ollama ollama list
```

### "Redis connection failed"

**Check:**
- Redis is running: `docker compose ps redis`
- Password in `.env` matches: `STORAGE_CONFIG__PASSWORD`
- Port is available: `netstat -an | grep 6379`
- Check logs: `docker compose logs redis`

### "Bot not responding"

**Check:**
1. Bot token is valid: `NOTIFICATION_CONFIG__BOT_TOKEN`
2. Chat ID is correct: `NOTIFICATION_CONFIG__CHAT_ID`
3. Bot is running: `docker compose ps backend`
4. Check logs: `docker compose logs backend -f`
5. Test bot manually: Send `/start` in Telegram

### "Loki unavailable"

**Solution:**
```bash
# Check Loki is running
curl http://localhost:3100/ready

# Verify configuration
# LOG_SOURCE_CONFIG__URL should match Loki URL
# LOG_SOURCE_CONFIG__APP_NAME should match your app's label

# Check Loki logs
docker compose logs loki

# Test query manually
curl -G "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={app="your-app-name"}' \
  --data-urlencode "start=$(date -u -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date -u +%s)000000000"
```

### "Rate limit exceeded"

This is normal behavior. Wait for the cooldown period (shown in the error message) or contact admin to reset limits.

### Docker build fails

```bash
# Clean Docker cache
docker compose down -v
docker system prune -a

# Rebuild from scratch
docker compose build --no-cache
docker compose up
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create your feature branch (`git switch -c feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality

Before submitting:
```bash
# Run linters
uv run ruff check --fix
uv run ruff format

# Type checking
uv run ty check src/

# Pre-commit hooks
uv run pre-commit run --all-files
```

## Support

- 📧 **Issues**: [GitHub Issues](https://github.com/SokolovG/flarity/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/SokolovG/flarity/discussions)
- ⭐ **Star the repo** if you find it useful!
- 📨 **Contact**: Email me at `sokolov_gr@proton.me` or contact me on Telegram at ``sokolov_gr`.

**Made by [Grigoriy Sokolov](https://github.com/SokolovG)**
