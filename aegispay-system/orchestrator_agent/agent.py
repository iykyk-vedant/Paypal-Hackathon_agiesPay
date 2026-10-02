# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import json
import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
import uvicorn
import httpx
from a2a.client.legacy import A2AClient
from a2a.types import (
    JSONRPCErrorResponse,
    Message,
    MessageSendParams,
    Role,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
    TextPart,
)
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get config from environment variables
INVESTIGATION_AGENT_URL = os.environ.get(
    "INVESTIGATION_AGENT_SERVICE_URL",
    "http://investigation-agent-service",
)
ACTUATOR_AGENT_URL = os.environ.get(
    "ACTUATOR_AGENT_SERVICE_URL",
    "http://actuator-agent-service",
)
RISK_SCORE_THRESHOLD = os.environ.get("RISK_SCORE_THRESHOLD", "7")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ORCHESTRATOR_PROMPT_TEMPLATE = """
You are AegisPay Orchestrator, the command agent coordinating fraud investigations for PayPal commerce transactions.
Follow this doctrine for every transaction alert:
1. Always invoke the InvestigationAgent tool first, passing the raw transaction JSON so it can produce a case file with a risk score.
2. Review the investigation response. The escalation threshold for risky activity is {threshold}.
3. If the risk score is greater than or equal to {threshold}, call the ActuatorAgent tool exactly once with JSON of the form {{"action": "lock_account", "account_id": "<ACCOUNT_ID>", "ext_user_id": "<EXT_USER_ID>", "reason": "<SHORT_REASON>", "case_file": <CASE_FILE> }}. The GenAI toolbox expects the `account_id` field; include `ext_user_id` when available.
4. If the risk score is below the threshold, do not actuate; instead, summarize why no action was taken.
5. Conclude with a concise narrative summary that states the risk score, whether actuation occurred, and the supporting justification.
Do not send alternative keys such as "command". Avoid repeated actuator calls after a successful response.
"""

# Cache for downstream A2A clients keyed by agent label.
_client_registry: dict[str, A2AClient] = {}

_TOOL_LABELS = {
    "delegate_to_investigation_agent": "InvestigationAgent",
    "delegate_to_actuator_agent": "ActuatorAgent",
}


_latest_case_file: Any | None = None


def _human_tool_name(raw_name: str) -> str:
    return _TOOL_LABELS.get(raw_name, raw_name)


def _extract_tool_response(tool_events: list[dict[str, Any]], tool_label: str) -> Any:
    for event in reversed(tool_events):
        if event.get("tool") == tool_label and event.get("event") == "response":
            return event.get("response")
    return None


def _get_or_create_client(cache_key: str, url: str) -> A2AClient | None:
    """Return a cached A2A client or create a new one for the target URL."""
    client = _client_registry.get(cache_key)
    if client is not None:
        return client

    try:
        httpx_client = httpx.AsyncClient(timeout=30.0)
        client = A2AClient(httpx_client=httpx_client, url=url)
        _client_registry[cache_key] = client
        logger.info("Created A2A client for %s at %s", cache_key, url)
        return client
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error(
            "Failed to create A2A client for %s at %s: %s",
            cache_key,
            url,
            exc,
            exc_info=True,
        )
        return None


def _extract_text_from_message(message: Message) -> str:
    """Combine all text parts from an A2A message into a single string."""
    texts: list[str] = []
    if message.parts:
        for part in message.parts:
            text_value = None
            if hasattr(part, "root") and hasattr(part.root, "text"):
                text_value = part.root.text
            elif hasattr(part, "text"):
                text_value = part.text
            if text_value:
                texts.append(text_value.strip())
    return "\n".join(filter(None, texts))


def _maybe_extract_json_payload(raw_text: str) -> Any | None:
    """Attempt to parse JSON content from an agent text response."""
    candidates: list[str] = []
    normalized = raw_text.strip()
    if normalized:
        candidates.append(normalized)
        colon_index = normalized.find(":")
        if colon_index != -1 and colon_index + 1 < len(normalized):
            candidates.append(normalized[colon_index + 1 :].strip())

    for candidate in candidates:
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def _format_agent_result(agent_label: str, response: SendMessageResponse) -> dict[str, Any]:
    """Normalize SendMessageResponse into a JSON-serializable payload."""
    if response is None:
        return {"agent": agent_label, "error": "No response from agent"}

    root = response.root
    if isinstance(root, JSONRPCErrorResponse):
        error_payload = {"agent": agent_label, "error": "Remote agent returned an error"}
        if root.error:
            error_payload["code"] = root.error.code
            error_payload["message"] = root.error.message
            if root.error.data is not None:
                error_payload["data"] = root.error.data
        return error_payload

    result = root.result
    if isinstance(result, Message):
        text_content = _extract_text_from_message(result)
        payload: dict[str, Any] = {
            "agent": agent_label,
            "raw_message": text_content,
        }
        parsed = _maybe_extract_json_payload(text_content)
        if parsed is not None:
            payload["data"] = parsed
        return payload

    if isinstance(result, Task):
        return {
            "agent": agent_label,
