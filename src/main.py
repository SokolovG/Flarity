import asyncio
import logging
import sys
from datetime import datetime

import httpx
from dishka import make_async_container

from src.core import MyProvider
from src.exceptions import ServiceNotReadyError
from src.services import LogAnalysisService

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("src").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


async def send_fake_logs_to_loki(loki_url: str, app_name: str) -> None:
    push_url = f"{loki_url}/loki/api/v1/push"

    now_ns = str(int(datetime.now().timestamp() * 1_000_000_000))

    payload = {
        "streams": [
            {
                "stream": {"app": app_name, "level": "error", "service": "backend"},
                "values": [
                    [
                        now_ns,
                        "Database connection timeout: failed to connect to postgres at localhost:5432",
                    ],
                    [now_ns, "Database connection timeout: connection refused after 30s"],
                    [
                        now_ns,
                        "API rate limit exceeded: 429 Too Many Requests from client 192.168.1.100",
                    ],
                    [
                        now_ns,
                        "API rate limit exceeded: 429 Too Many Requests from client 192.168.1.101",
                    ],
                    [now_ns, "Null pointer exception in user service: user.email is null"],
                    [now_ns, "Null pointer exception in user service: user.profile is null"],
                    [now_ns, "Redis connection failed: ECONNREFUSED 127.0.0.1:6379"],
                    [now_ns, "Authentication failed: invalid JWT token signature"],
                    [now_ns, "Authentication failed: JWT token expired"],
                    [now_ns, "File not found: /var/app/uploads/user_avatar_123.png"],
                ],
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(push_url, json=payload, timeout=10)
            if response.status_code == 204:
                logger.info(
                    f"Successfully sent {len(payload['streams'][0]['values'])} test logs to Loki"
                )
            else:
                logger.error(f"Failed to send logs: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error sending logs to Loki: {e}")


async def main() -> None:
    container = make_async_container(MyProvider())

    try:
        # settings = await container.get(Settings)

        # logger.info("Sending fake logs to Loki...")
        # await send_fake_logs_to_loki(settings.LOKI_URL, settings.LOKI_APP_NAME)

        # logger.info("Waiting 10 seconds for Loki to index logs...")
        # await asyncio.sleep(10)

        log_analyzer_service = await container.get(LogAnalysisService)

        ready = await log_analyzer_service.check_readiness()
        if not ready:
            logger.error("Services not ready!")
            return

        logger.info("Starting log analysis...")
        await log_analyzer_service.analyze_and_notify()

    except ServiceNotReadyError as e:
        logger.error(f"Services failed to become ready: {e}")

    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
