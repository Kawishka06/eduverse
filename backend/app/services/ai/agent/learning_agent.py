"""EduVerse Learning Agent — ReAct loop with tools via fal.ai LLM."""

from __future__ import annotations

from functools import lru_cache

from app.config import Settings, get_settings
from app.services.ai.agent.json_utils import extract_json_object
from app.services.ai.agent.models import AgentResult, AgentStep
from app.services.ai.agent.prompts import build_agent_system_prompt
from app.services.ai.agent.tools import ToolRegistry
from app.services.ai.exceptions import LLMError
from app.services.ai.helpers.fal import configure_fal_key, run_fal_model
from app.services.ai.helpers.llm import _extract_llm_text, mock_tutor_answer


class EduVerseLearningAgent:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        configure_fal_key(self.settings.fal_key)
        self.tools = ToolRegistry(self.settings)

    async def chat(
        self,
        message: str,
        *,
        mode: str = "standard",
        character_persona: str | None = None,
        material_context: str | None = None,
    ) -> AgentResult:
        message = message.strip()
        if not message:
            raise ValueError("Message cannot be empty")

        mode = mode if mode in ("standard", "simple", "meme") else "standard"
        steps: list[AgentStep] = []

        if self.settings.fal_mock_mode or not self.settings.fal_key:
            answer = mock_tutor_answer(message, mode)
            if character_persona:
                answer = f"*Speaking as your lesson character*\n\n{answer}"
            return AgentResult(
                answer=answer,
                message=message,
                model="mock",
                mode=mode,
                steps=steps,
                context_used=bool(material_context),
            )

        system_prompt = build_agent_system_prompt(
            mode,
            character_persona=character_persona,
            material_context=material_context,
        )

        conversation = f"Student message:\n{message}\n"
        max_turns = self.settings.agent_max_turns

        for _turn in range(max_turns):
            raw = await self._llm_turn(system_prompt, conversation)
            parsed = extract_json_object(raw)

            if not parsed:
                retry_raw = await self._llm_turn(
                    system_prompt + "\nYou MUST reply with valid JSON only.",
                    conversation,
                )
                parsed = extract_json_object(retry_raw)
                if not parsed:
                    return AgentResult(
                        answer=raw.strip() or "I could not process that request.",
                        message=message,
                        model=self.settings.fal_llm_model,
                        mode=mode,
                        steps=steps,
                        context_used=bool(material_context),
                    )

            action = str(parsed.get("action", "")).lower()

            if action == "answer":
                content = str(parsed.get("content", "")).strip()
                return AgentResult(
                    answer=content or raw.strip(),
                    message=message,
                    model=self.settings.fal_llm_model,
                    mode=mode,
                    steps=steps,
                    context_used=bool(material_context),
                )

            if action == "tool":
                tool_name = str(parsed.get("name", "")).strip()
                tool_input = parsed.get("input")
                if not isinstance(tool_input, dict):
                    tool_input = {}

                output = await self.tools.execute(tool_name, tool_input)
                steps.append(
                    AgentStep(
                        step_type="tool",
                        tool_name=tool_name,
                        input=tool_input,
                        output=output[:2000],
                    ),
                )
                conversation += (
                    f"\nTool call: {tool_name}\n"
                    f"Input: {tool_input}\n"
                    f"Tool result:\n{output}\n"
                    'Continue — use another tool or respond with {"action":"answer","content":"..."}.\n'
                )
                continue

            return AgentResult(
                answer=raw.strip(),
                message=message,
                model=self.settings.fal_llm_model,
                mode=mode,
                steps=steps,
                context_used=bool(material_context),
            )

        return AgentResult(
            answer="I reached the maximum reasoning steps. Please try a simpler question.",
            message=message,
            model=self.settings.fal_llm_model,
            mode=mode,
            steps=steps,
            context_used=bool(material_context),
        )

    async def _llm_turn(self, system_prompt: str, user_content: str) -> str:
        try:
            result = await run_fal_model(
                self.settings.fal_llm_endpoint,
                {
                    "model": self.settings.fal_llm_model,
                    "prompt": user_content,
                    "system_prompt": system_prompt,
                    "max_tokens": self.settings.fal_llm_max_tokens,
                },
                timeout=self.settings.fal_request_timeout,
            )
        except Exception as exc:
            raise LLMError(f"Agent LLM request failed: {exc}") from exc

        text = _extract_llm_text(result)
        if not text:
            raise LLMError("LLM returned an empty response")
        return text


@lru_cache
def get_learning_agent() -> EduVerseLearningAgent:
    return EduVerseLearningAgent()
