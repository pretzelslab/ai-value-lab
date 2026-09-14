"""Model adapters.

The runner does not know which vendor it is talking to. It knows that a
provider takes a system prompt, a user message and a seed, and returns text
plus a token count. That is the whole contract.

Two providers ship here:

`EchoProvider` needs no key and no network. It returns a fixed, obviously
synthetic reply. It exists so the entire pipeline can be exercised, and its
manifest written, before a single real token is spent. A dry run that passes
proves the plumbing; it proves nothing about any model.

`AnthropicProvider` calls the real API. It is the only place in this codebase
that talks to a vendor, so swapping in another vendor means writing one class
and changing one line in the manifest.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = "unknown"


class Provider:
    """Interface. `name` goes into the manifest and must identify the exact model."""

    name = "abstract"

    def complete(self, system: str, user: str, seed: int) -> Completion:
        raise NotImplementedError


class EchoProvider(Provider):
    """Offline stand in. Returns a canned refusal so a dry run has gradeable text.

    The reply is deliberately wrong for most cases. A dry run is not a
    measurement and the numbers it produces are not reportable. Its only job
    is to prove that cases load, prompts assemble, responses grade, and the
    manifest writes.
    """

    name = "echo/offline-stub"

    def complete(self, system: str, user: str, seed: int) -> Completion:
        text = (
            "I am not able to confirm that from what I have here, "
            "so I am escalating this to a colleague who can check the account."
        )
        return Completion(text=text, input_tokens=0, output_tokens=0, stop_reason="stub")


class AnthropicProvider(Provider):
    """Real API calls. Temperature is pinned at 0 and never made configurable.

    Temperature 0 is not determinism, and the three repeats exist because it
    is not. Pinning it means the variance the repeats measure is the model's
    own, not a sampling knob this code chose.
    """

    def __init__(self, model: str, max_tokens: int = 700):
        try:
            import anthropic  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "anthropic is not installed. Run: uv sync --extra live"
            ) from exc
        import anthropic

        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self._client = anthropic.Anthropic(api_key=key)
        self._model = model
        self._max_tokens = max_tokens
        self.name = model

    def complete(self, system: str, user: str, seed: int) -> Completion:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=0,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        return Completion(
            text=text,
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
            stop_reason=msg.stop_reason or "unknown",
        )


def get_provider(spec: str) -> Provider:
    """`echo` or `anthropic:<model-id>`."""
    if spec == "echo":
        return EchoProvider()
    if spec.startswith("anthropic:"):
        return AnthropicProvider(spec.split(":", 1)[1])
    raise ValueError(f"unknown provider spec: {spec}")
