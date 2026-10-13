from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_env_example_exists() -> None:
    assert (REPO_ROOT / ".env.example").is_file()


def test_docker_compose_defines_postgres_with_healthcheck() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "pgvector/pgvector" in compose
    assert "healthcheck:" in compose
    assert "postgres_data:" in compose


def test_bootstrap_scripts_exist() -> None:
    scripts = REPO_ROOT / "scripts"
    assert (scripts / "bootstrap.sh").is_file()
    assert (scripts / "verify-setup.sh").is_file()
    assert (scripts / "fresh-install.sh").is_file()


def test_portfolio_docs_exist() -> None:
    assert (REPO_ROOT / "docs" / "architecture.md").is_file()
    assert (REPO_ROOT / "docs" / "sample-investigation.md").is_file()
    assert (REPO_ROOT / "docs" / "screenshots" / "payments-list.svg").is_file()
    assert (REPO_ROOT / "docs" / "screenshots" / "investigation-result.svg").is_file()


@pytest.mark.parametrize(
    "script",
    ["bootstrap.sh", "verify-setup.sh", "fresh-install.sh"],
)
def test_scripts_are_executable(script: str) -> None:
    path = REPO_ROOT / "scripts" / script
    assert path.stat().st_mode & 0o111, f"{script} should be executable"
