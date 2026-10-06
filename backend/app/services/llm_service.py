"""
AI Agent Guardian - LLM Service Abstraction Layer (V1 Foundation -> V2+ NVIDIA/Kimi Integration)

This module isolates the AI/LLM provider from the core security platform.
In Version 1: Operates in offline/deterministic mode using rule-based security intent parsing.
In Version 2+: Supports OpenAI-compatible providers such as NVIDIA and Kimi/K3 through a single interface.
"""

from typing import List, Dict, Any, Optional

import httpx

from ..core.config import settings


class LLMService:
    """Unified LLM Service interface for AI Agent Guardian."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, provider: Optional[str] = None):
        self.provider = (provider or settings.LLM_PROVIDER or "").lower() or self._detect_provider(api_key)
        if self.provider == "kimi":
            self.api_key = api_key or settings.KIMI_API_KEY
            self.model = model or settings.KIMI_MODEL
            self.base_url = settings.KIMI_BASE_URL.rstrip("/")
        elif self.provider == "nvidia":
            self.api_key = api_key or settings.NVIDIA_API_KEY
            self.model = model or settings.NVIDIA_MODEL
            self.base_url = "https://integrate.api.nvidia.com/v1"
        else:
            self.api_key = api_key or settings.KIMI_API_KEY or settings.NVIDIA_API_KEY
            self.model = model or settings.KIMI_MODEL or settings.NVIDIA_MODEL
            self.base_url = settings.KIMI_BASE_URL.rstrip("/") if settings.KIMI_API_KEY else "https://integrate.api.nvidia.com/v1"
            self.provider = "mock_v1" if not self.api_key or self.api_key.startswith("mock") else ("kimi" if settings.KIMI_API_KEY else "nvidia")

    def _detect_provider(self, api_key: Optional[str]) -> str:
        key = (api_key or "").lower()
        if settings.LLM_PROVIDER:
            return settings.LLM_PROVIDER.lower()
        if key.startswith("kimi") or settings.KIMI_API_KEY:
            return "kimi"
        if key.startswith("nvapi") or key.startswith("nvidia") or settings.NVIDIA_API_KEY:
            return "nvidia"
        return "mock_v1"

    def is_llm_active(self) -> bool:
        """Indicates if an external LLM provider is configured and active."""
        return self.provider in {"nvidia", "kimi"} and bool(self.api_key)

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate conversational security response.
        In V1: Returns structured fallback response directing to the deterministic chat engine.
        In V2+: Calls an external OpenAI-compatible API if configured.
        """
        if self.is_llm_active():
            try:
                if self.provider == "kimi":
                    return await self._call_kimi_api(prompt, system_prompt, context, tools)
                if self.provider == "nvidia":
                    return await self._call_nvidia_api(prompt, system_prompt, context, tools)
            except (ConnectionError, OSError, httpx.HTTPError, httpx.TimeoutException, TimeoutError) as exc:
                return {
                    "mode": "deterministic_v1",
                    "provider": "Guardian-Rule-Engine",
                    "message": "External model request failed due to connectivity, firewall, or bad credentials; falling back to the Guardian deterministic engine.",
                    "error": str(exc),
                    "fallback": True,
                }

        return {
            "mode": "deterministic_v1",
            "provider": "Guardian-Rule-Engine",
            "message": "Processed via Guardian Deterministic Intent Engine.",
        }

    async def _call_kimi_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Call a Kimi or Moonshot-compatible chat completion endpoint."""
        if not self.api_key:
            raise ConnectionError("No Kimi API key configured.")

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            for item in context:
                role = item.get("role", "user")
                content = item.get("content", "")
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            response_json = response.json()

        content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            raise ConnectionError("Kimi returned an empty response payload.")

        return {
            "mode": "remote",
            "provider": "kimi",
            "model": self.model,
            "message": content.strip(),
        }

    async def _call_nvidia_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Placeholder for NVIDIA NIM / OpenAI-compatible endpoint integration in V2."""
        # Endpoint: https://integrate.api.nvidia.com/v1/chat/completions
        raise NotImplementedError("NVIDIA API integration is scheduled for Version 2.")


# Singleton service instance
llm_service = LLMService()
