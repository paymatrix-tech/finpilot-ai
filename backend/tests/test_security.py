from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.security.tools import READ_ONLY_INVESTIGATION_TOOL_NAMES, assert_read_only_tool
from app.security.validation import validate_payment_id
from app.tools.definitions import PAYMENT_INVESTIGATION_TOOLS
from app.tools.exceptions import ToolError
from app.tools.executor import PaymentToolExecutor
from app.tools.payment import PaymentTools
from app.repositories.payment import PaymentRepository


def test_payment_id_validation_accepts_seed_style_ids() -> None:
    assert validate_payment_id("PAY-1001") == "PAY-1001"
    assert validate_payment_id("PAY-TEST-1001") == "PAY-TEST-1001"


def test_payment_id_validation_rejects_injection_like_values() -> None:
    with pytest.raises(ValueError):
        validate_payment_id("PAY-1001; DROP TABLE payments;--")
    with pytest.raises(ValueError):
        validate_payment_id("../etc/passwd")


def test_read_only_tool_allowlist_matches_definitions() -> None:
    defined = {item["function"]["name"] for item in PAYMENT_INVESTIGATION_TOOLS}
    assert READ_ONLY_INVESTIGATION_TOOL_NAMES == frozenset(defined)


def test_executor_rejects_unknown_and_write_like_tools(db) -> None:
    executor = PaymentToolExecutor(PaymentTools(PaymentRepository(db)))
    result = executor.execute("delete_payment", {"payment_id": "PAY-1001"})
    assert result["error"] == "tool_error"

    with pytest.raises(ToolError):
        assert_read_only_tool("run_sql_update")


def test_api_rejects_invalid_payment_id_path(client: TestClient) -> None:
    response = client.get("/api/payments/not-a-payment-id")
    assert response.status_code == 422


def test_investigation_rejects_invalid_payment_id_before_agent(client: TestClient) -> None:
    response = client.post(
        "/api/investigations",
        json={"payment_id": "bad-id", "question": "Why did this fail?"},
    )
    assert response.status_code == 422


def test_env_file_is_gitignored() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore


def test_env_file_is_not_tracked() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    env_path = repo_root / ".env"
    if env_path.is_file():
        import subprocess

        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", ".env"],
            cwd=repo_root,
            capture_output=True,
            check=False,
        )
        assert tracked.returncode != 0
