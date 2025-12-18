import json
from datetime import datetime
import logging
import httpx

from src.core.settings.app_settings import AppSettings

logger = logging.getLogger(__name__)


async def send_fake_logs_to_loki() -> None:
    settings = AppSettings()
    loki_url = settings.log_source.loki_url
    app_name = settings.log_source.loki_app_name

    logger.info("Sending fake logs to Loki...")
    push_url = f"{loki_url}/loki/api/v1/push"

    now_ns = str(int(datetime.now().timestamp() * 1_000_000_000))

    fake_logs = [
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "Database connection timeout: failed to connect to postgres",
            "target": "ogonek_db::connection",
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "Database connection timeout: connection refused after 30s",
            "target": "ogonek_db::connection",
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "API rate limit exceeded: 429 Too Many Requests",
            "target": "ogonek_server::api::middleware",
            "span": {
                "method": "GET",
                "request_id": "test-req-001",
                "uri": "/api/v1/lessons",
                "name": "http_request"
            }
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "API rate limit exceeded: 429 Too Many Requests",
            "target": "ogonek_server::api::middleware",
            "span": {
                "method": "POST",
                "request_id": "test-req-002",
                "uri": "/api/v1/auth/refresh",
                "name": "http_request"
            }
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "Null pointer exception in user service: user.email is null",
            "target": "ogonek_server::services::user",
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "Null pointer exception in user service: user.profile is null",
            "target": "ogonek_server::services::user",
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "Redis connection failed: ECONNREFUSED",
            "target": "ogonek_cache::redis",
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "Authentication failed: invalid JWT token signature",
            "target": "ogonek_server::auth::jwt",
            "span": {
                "method": "POST",
                "request_id": "test-req-003",
                "uri": "/api/v1/auth/login",
                "name": "http_request"
            }
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "Authentication failed: JWT token expired",
            "target": "ogonek_server::auth::jwt",
            "span": {
                "method": "GET",
                "request_id": "test-req-004",
                "uri": "/api/v1/state/context",
                "name": "http_request"
            }
        },
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "ERROR",
            "message": "File not found: /var/app/uploads/user_avatar_123.png",
            "target": "ogonek_server::storage::s3",
        },
    ]

    json_payload = {
        "streams": [
            {
                "stream": {"app": app_name, "level": "error", "service": "backend"},
                "values": [[now_ns, json.dumps(log)] for log in fake_logs],
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(push_url, json=json_payload, timeout=10)
            if response.status_code == 204:
                logger.info(
                    f"Successfully sent {len(fake_logs)} test logs to Loki"
                )
            else:
                logger.error(f"Failed to send logs: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Error sending logs to Loki: {e}")
