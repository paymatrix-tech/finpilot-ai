from typing import Any

PAYMENT_INVESTIGATION_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_payment",
            "description": (
                "Load the payment record for a payment_id. Use first to confirm status, "
                "amount, currency, gateway, payment_method, and error_code. "
                "Required before interpreting failures."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "Payment identifier from the investigation request, e.g. PAY-1001.",
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
            "description": (
                "Load ordered lifecycle events for a payment (created, validated, gateway request/response, "
                "failure/success). Use when status or error_code alone does not explain the failure path "
                "or you need timestamps and gateway metadata."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "Same payment_id used in get_payment.",
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
            "description": (
                "Search structured application logs for a payment. Use after get_payment when you need "
                "service-level errors, gateway messages, timeouts, or decline reasons. "
                "Pass a short query such as an error_code (R01), 'timeout', 'gateway', or 'declined'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "Payment identifier to scope log search.",
                    },
                    "query": {
                        "type": "string",
                        "description": (
                            "Optional filter matched against log message, service name, or level. "
                            "Prefer specific keywords from error_code or events."
                        ),
                    },
                },
                "required": ["payment_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_payment_docs",
            "description": (
                "Semantic search over internal payment operations docs (ACH/card codes, retry policy, "
                "gateway runbooks, timeouts). Use when you have an error code or symptom and need "
                "official meaning, retry rules, or escalation guidance. Returns chunks with source file names."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Natural language or keywords, e.g. 'R01 insufficient funds', "
                            "'gateway timeout retry', 'card decline code 05'."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max documentation chunks to return (default 5, max 10).",
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": ["query"],
            },
        },
    },
]
