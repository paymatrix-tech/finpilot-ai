from app.llm.groq_models import resolve_groq_model


def test_resolve_groq_model_maps_retired_llama() -> None:
    assert resolve_groq_model("llama-3.3-70b-versatile") == "openai/gpt-oss-120b"


def test_resolve_groq_model_keeps_current_id() -> None:
    assert resolve_groq_model("openai/gpt-oss-120b") == "openai/gpt-oss-120b"
