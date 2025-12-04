
from datetime import datetime
import logging

import httpx

from src.core.settings.app_settings import AppSettings


logger = logging.getLogger(__name__)


async def send_fake_logs_to_loki() -> None:
    #TODO: добавить тож самое но в json
    settings = AppSettings()

    loki_url = settings.log_source.loki_url
    app_name = settings.log_source.loki_app_name

    logger.info("Sending fake logs to Loki...")
    push_url = f"{loki_url}/loki/api/v1/push"

    now_ns = str(int(datetime.now().timestamp() * 1_000_000_000))

    str_payload = {
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
            response = await client.post(push_url, json=str_payload, timeout=10)
            if response.status_code == 204:
                logger.info(
                    f"Successfully sent {len(str_payload['streams'][0]['values'])} test logs to Loki"
                )
            else:
                logger.error(f"Failed to send logs: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error sending logs to Loki: {e}")
