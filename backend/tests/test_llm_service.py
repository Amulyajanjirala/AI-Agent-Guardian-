import asyncio

from backend.app.services.llm_service import LLMService


def test_kimi_provider_is_detected_and_used(monkeypatch):
    service = LLMService(api_key="kimi-test-key", model="moonshot-v1-32k")
    assert service.provider == "kimi"

    async def fake_call(*args, **kwargs):
        return {
            "mode": "remote",
            "provider": "kimi",
            "message": "Kimi call succeeded",
        }

    monkeypatch.setattr(service, "_call_kimi_api", fake_call)
    result = asyncio.run(service.generate_response("hello"))

    assert result["provider"] == "kimi"
    assert result["message"] == "Kimi call succeeded"


def test_kimi_network_failure_falls_back_cleanly(monkeypatch):
    service = LLMService(api_key="kimi-test-key", model="moonshot-v1-32k")

    async def fake_call(*args, **kwargs):
        raise ConnectionError("Firewall or network blocked the Kimi request")

    monkeypatch.setattr(service, "_call_kimi_api", fake_call)
    result = asyncio.run(service.generate_response("hello"))

    assert result["mode"] == "deterministic_v1"
    assert result["provider"] == "Guardian-Rule-Engine"
