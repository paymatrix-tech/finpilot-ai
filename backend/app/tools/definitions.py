from typing import Any

PAYMENT_INVESTIGATION_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_payment",
            "description": "Fetch payment details including amount, currency, status, gateway, and error code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "Payment identifier, for example PAY-1001.",
                    },
                },
                "required": ["payment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_payment_events",
            "description": "Fetch lifecycle events for a payment such as creation, validation, and gateway responses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "Payment identifier.",
                    },
                },
                "required": ["payment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_logs",
            "description": "Search application logs for a payment. Use query to filter by message, service, or level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "Payment identifier.",
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional text to search within log message, service, or level.",
                    },
                },
                "required": ["payment_id"],
            },
        },
    },
]
