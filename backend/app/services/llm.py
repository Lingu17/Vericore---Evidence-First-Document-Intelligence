"""
LLM Provider Abstraction & Groq Provider Service.
Optimized for minimum token usage: query answer caching, adaptive history pruning,
zero-reasoning direct JSON output, strict local source-id validation, and token usage logging.
"""

from abc import ABC, abstractmethod
import hashlib
import json
import re
from typing import Any, Optional
from groq import Groq
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import (
    ChatMessage,
    ChatResponse,
    ChatStatus,
    ConfidenceLevel,
    SourceEvidence,
)
from app.prompts.qa_prompt import SYSTEM_PROMPT, build_user_prompt
from app.services.confidence import calculate_evidence_confidence
from app.services.retriever import normalize_query_text


FOLLOW_UP_PRONOUNS = {
    "that", "them", "it", "they", "those", "these", "this", "their", "its",
    "after that", "what about", "and also", "how about", "why is that"
}


def is_follow_up_question(question: str) -> bool:
    """Detects whether a question is dependent on previous conversation history."""
    q_lower = question.lower()
    words = set(re.findall(r"\b\w+\b", q_lower))
    if any(p in words for p in ["that", "them", "it", "those", "these", "they", "its"]):
        return True
    if any(phrase in q_lower for phrase in ["what about", "how about", "after that", "and also"]):
        return True
    return False


def generate_cache_key(
    normalized_question: str,
    document_scope: Optional[str],
    source_ids: list[str]
) -> str:
    """Generates unique deterministic hash for identical question + evidence pairs."""
    joined_sources = ",".join(sorted(source_ids))
    raw = f"{normalized_question}|{document_scope or 'all'}|{joined_sources}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class LLMProvider(ABC):
    @abstractmethod
    def generate_answer(
        self,
        question: str,
        sources: list[SourceEvidence],
        conversation_history: list[ChatMessage],
        document_scope: Optional[str] = None
    ) -> ChatResponse:
        pass


class GroqProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.client: Optional[Groq] = None
        self._answer_cache: dict[str, ChatResponse] = {}

        if self.api_key and not settings.USE_MOCK_LLM:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info(f"GroqProvider initialized with model '{self.model}'.")
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")
        else:
            logger.info("Groq API client offline/mock mode. Deterministic grounded engine active.")

    def _format_conversation_history(self, question: str, history: list[ChatMessage]) -> str:
        """
        Retains conversation context ONLY if question is an ambiguous follow-up.
        Limits to MAX_HISTORY_MESSAGES (last 1-2 turns).
        """
        if not history or not is_follow_up_question(question):
            return ""

        recent = history[-settings.MAX_HISTORY_MESSAGES:]
        formatted = []
        for msg in recent:
            role = "User" if msg.role == "user" else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

    def _parse_llm_json(self, raw_output: str) -> dict[str, Any]:
        """Safely parses structured JSON response from LLM."""
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass

        return {
            "status": "answered",
            "answer": cleaned,
            "source_ids": []
        }

    def _fallback_local_generation(
        self,
        question: str,
        sources: list[SourceEvidence]
    ) -> ChatResponse:
        """Deterministic local fallback synthesizing exact excerpts from retrieved evidence."""
        if not sources:
            return ChatResponse(
                status=ChatStatus.NOT_FOUND,
                answer="I couldn't find supporting information for this question in the uploaded documents.",
                confidence=ConfidenceLevel.LOW,
                sources=[]
            )

        confidence = calculate_evidence_confidence(sources)
        if confidence == ConfidenceLevel.LOW:
            return ChatResponse(
                status=ChatStatus.NOT_FOUND,
                answer="I couldn't find sufficient supporting evidence in the uploaded documents.",
                confidence=ConfidenceLevel.LOW,
                sources=[]
            )

        top_source = sources[0]
        # Keep answer concise (max ~250 chars)
        answer_text = top_source.evidence[:240].strip()
        if len(top_source.evidence) > 240:
            answer_text += "..."

        return ChatResponse(
            status=ChatStatus.ANSWERED,
            answer=answer_text,
            confidence=confidence,
            sources=sources
        )

    def generate_answer(
        self,
        question: str,
        sources: list[SourceEvidence],
        conversation_history: list[ChatMessage],
        document_scope: Optional[str] = None
    ) -> ChatResponse:
        # 1. Hallucination gate: No sources -> return NOT_FOUND immediately (0 LLM tokens)
        if not sources:
            return ChatResponse(
                status=ChatStatus.NOT_FOUND,
                answer="I couldn't find supporting information for this question in the uploaded documents.",
                confidence=ConfidenceLevel.LOW,
                sources=[]
            )

        # 2. Check Answer Cache for identical question + evidence
        norm_q = normalize_query_text(question)
        source_ids = [s.chunk_id for s in sources]
        cache_key = generate_cache_key(norm_q, document_scope, source_ids)

        if cache_key in self._answer_cache:
            logger.info(f"Answer Cache HIT for query: '{norm_q[:40]}'. Reusing cached response (0 tokens).")
            return self._answer_cache[cache_key]

        # 3. Check if live Groq API is active
        if not self.client or not self.api_key or settings.USE_MOCK_LLM:
            res = self._fallback_local_generation(question, sources)
            self._answer_cache[cache_key] = res
            return res

        # 4. Build minimal prompt (adaptive history pruning)
        history_str = self._format_conversation_history(question, conversation_history)
        user_prompt = build_user_prompt(question, sources, history_str)

        # 5. Call Groq with Temperature=0, Max Tokens=250
        try:
            logger.info(
                f"Calling Groq ('{self.model}') with {len(sources)} adaptive chunk(s), "
                f"temp={settings.TEMPERATURE}, max_tokens={settings.MAX_OUTPUT_TOKENS}..."
            )
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                response_format={"type": "json_object"}
            )

            # Log token usage
            if hasattr(response, "usage") and response.usage:
                u = response.usage
                logger.info(
                    f"LLM_USAGE prompt={u.prompt_tokens} completion={u.completion_tokens} total={u.total_tokens}"
                )

            raw_content = response.choices[0].message.content or ""
            parsed_data = self._parse_llm_json(raw_content)

            status_str = parsed_data.get("status", "answered").lower()
            status = ChatStatus.NOT_FOUND if status_str == "not_found" else ChatStatus.ANSWERED
            answer = parsed_data.get("answer", "").strip()
            cited_source_ids = parsed_data.get("source_ids", [])

            if status == ChatStatus.NOT_FOUND:
                res = ChatResponse(
                    status=ChatStatus.NOT_FOUND,
                    answer=answer or "I couldn't find supporting information in the uploaded documents.",
                    confidence=ConfidenceLevel.LOW,
                    sources=[]
                )
                self._answer_cache[cache_key] = res
                return res

            # 6. Validate source IDs locally: Keep ONLY verified retrieved chunks
            source_map = {s.chunk_id: s for s in sources}
            verified_sources = [source_map[sid] for sid in cited_source_ids if sid in source_map]
            if not verified_sources:
                verified_sources = sources

            confidence = calculate_evidence_confidence(verified_sources)

            res = ChatResponse(
                status=ChatStatus.ANSWERED,
                answer=answer,
                confidence=confidence,
                sources=verified_sources
            )
            self._answer_cache[cache_key] = res
            return res

        except Exception as e:
            logger.error(f"Groq API call error: {e}. Using deterministic grounded fallback.")
            res = self._fallback_local_generation(question, sources)
            self._answer_cache[cache_key] = res
            return res


llm_service: LLMProvider = GroqProvider()
