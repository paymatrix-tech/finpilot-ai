import json
import re
from typing import Any

_RETRY_IN_MESSAGE = re.compile(r"retry in (\d+(?:\.\d+)?)s", re.IGNORECASE)
_RETRY_DELAY = re.compile(r"^(\d+(?:\.\d+)?)s$", re.IGNORECASE)


def parse_retry_after_seconds(response_text: str) -> float | None:
    text = response_text.strip()
    if not text:
        return None

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return _retry_seconds_from_message(text)

    errors = payload if isinstance(payload, list) else [payload]
    for item in errors:
        if not isinstance(item, dict):
            continue
        retry = _retry_seconds_from_error_object(item.get("error", item))
        if retry is not None:
            return retry
    return _retry_seconds_from_message(text)


def _retry_seconds_from_error_object(error: Any) -> float | None:
    if not isinstance(error, dict):
        return None

    details = error.get("details")
    if isinstance(details, list):
        for detail in details:
            if not isinstance(detail, dict):
                continue
            retry_delay = detail.get("retryDelay")
            if isinstance(retry_delay, str):
                match = _RETRY_DELAY.match(retry_delay.strip())
                if match:
                    return float(match.group(1))

    return _retry_seconds_from_message(str(error.get("message", "")))


def _retry_seconds_from_message(message: str) -> float | None:
    match = _RETRY_IN_MESSAGE.search(message)
    if match:
        return float(match.group(1))
    return None
