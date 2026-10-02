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
            "task": result.model_dump(mode="json"),
        }

    return {"agent": agent_label, "result": result}


def _normalize_payload(payload: Any, agent_label: str) -> str | None:
    """Ensure payload is valid JSON and return it as a string."""
    if isinstance(payload, (dict, list, int, float, bool)) or payload is None:
        return json.dumps(payload)
    if isinstance(payload, str):
        candidate = payload.strip()
        if not candidate:
            return json.dumps({})
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            logger.warning(
                "Payload provided to %s delegate is not valid JSON: %s",
                agent_label,
                payload,
            )
            return None
        return json.dumps(parsed)

    logger.warning("Unsupported payload type %s for %s delegate", type(payload), agent_label)
    return None


def _parse_float(value: Any) -> Optional[float]:
    """Attempt to convert a value to float, returning None on failure."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        candidate = value.strip().replace("%", "")
        if not candidate:
            return None
        try:
            return float(candidate)
        except ValueError:
            return None
    return None


def _extract_risk_score(case_file: Any) -> Optional[float]:
    """Extract a numeric risk score from the investigation case file."""
    if not isinstance(case_file, dict):
        return None

    fraud_analysis = case_file.get("fraud_analysis")
    if isinstance(fraud_analysis, dict):
        score = _parse_float(fraud_analysis.get("risk_score"))
        if score is not None:
            return score

    # Some responses may return risk_score at the top level
    return _parse_float(case_file.get("risk_score"))


def _extract_justification(case_file: Any) -> Optional[str]:
    """Retrieve a textual justification from the case file if available."""
    if not isinstance(case_file, dict):
        return None

    fraud_analysis = case_file.get("fraud_analysis")
    if isinstance(fraud_analysis, dict):
        justification = fraud_analysis.get("justification")
        if isinstance(justification, str):
            return justification

    justification = case_file.get("justification")
    if isinstance(justification, str):
        return justification

    return None


def _extract_ext_user_id(case_file: Any) -> Optional[str]:
    """Extract ext_user_id from the case file using multiple heuristics."""
    if not isinstance(case_file, dict):
        return None

    transaction_data = case_file.get("transaction_data")
    if isinstance(transaction_data, dict):
        for key in ("ext_user_id", "user_id", "from_account_id"):
            value = transaction_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    user_details = case_file.get("user_details")
    if isinstance(user_details, dict):
        candidate = user_details.get("ext_user_id")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    elif isinstance(user_details, list):
        for entry in user_details:
            if isinstance(entry, dict):
                candidate = entry.get("ext_user_id")
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()

    return None


def _extract_account_id(case_file: Any) -> Optional[str]:
    """Extract an account identifier from the case file."""
    if not isinstance(case_file, dict):
        return None

    transaction_data = case_file.get("transaction_data")
    if isinstance(transaction_data, dict):
        for key in ("account_id", "from_account_id", "user_id"):
            value = transaction_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    user_details = case_file.get("user_details")
    if isinstance(user_details, dict):
        candidate = user_details.get("account_id") or user_details.get("ext_user_id")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    elif isinstance(user_details, list):
        for entry in user_details:
            if isinstance(entry, dict):
                candidate = entry.get("account_id") or entry.get("ext_user_id")
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()

    return None


def _maybe_extract_json_block(text: str) -> str | None:
    """Return the first JSON object substring found in text, if any."""
    stack: list[str] = []
    start: int | None = None
    for index, char in enumerate(text):
        if char == "{":
            if not stack:
                start = index
            stack.append(char)
        elif char == "}":
            if stack:
                stack.pop()
                if not stack and start is not None:
                    return text[start : index + 1]
    return None


def _coerce_to_dict(raw_command: Any) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    """Best-effort conversion of LLM output into a dictionary."""
    if isinstance(raw_command, dict):
        return dict(raw_command), None

    if not isinstance(raw_command, str):
        return None, f"Unsupported actuator payload type: {type(raw_command)}"

    text = raw_command.strip()
    # Strip leading tokens such as "execute_action:" or fenced code blocks.
    if text.lower().startswith("execute_action:"):
        text = text.split(":", 1)[1].strip()
    if text.startswith("```"):
        parts = text.split("```", 2)
        text = parts[1] if len(parts) > 1 else text.strip("`")
    if text.lower().startswith("json"):
        text = text[4:]
    text = text.strip("`").strip()

    candidates: list[str] = []
    block = _maybe_extract_json_block(text)
    if block:
        candidates.append(block)
    candidates.append(text)

    sanitized_candidates: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        sanitized_candidates.append(candidate)
        if "'" in candidate and '"' not in candidate:
            sanitized_candidates.append(candidate.replace("'", '"'))

    for candidate in sanitized_candidates:
        try:
            return json.loads(candidate), None
        except json.JSONDecodeError:
            continue

    logger.warning("Unable to coerce actuator payload into JSON: %s", raw_command)
    return None, "Actuator command must be valid JSON after sanitization."


def _prepare_actuator_payload(raw_command: Any) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    """Normalize LLM-provided actuator command payload."""
    payload, error = _coerce_to_dict(raw_command)
    if payload is None:
        return None, error

    case_file = payload.get("case_file")
    if case_file is None and _latest_case_file is not None:
        case_file = _latest_case_file
    account_id = payload.get("account_id") or payload.get("from_account_id")
    ext_user_id = payload.get("ext_user_id") or payload.get("user_id")

    if account_id is None and isinstance(case_file, dict):
        account_id = _extract_account_id(case_file)
    if ext_user_id is None and isinstance(case_file, dict):
        ext_user_id = _extract_ext_user_id(case_file)
        account_id = _extract_account_id(case_file)
    if account_id is None and ext_user_id is not None:
        account_id = ext_user_id

    if not account_id:
        return None, (
            "Actuator command missing account_id. Include the originating account_id from the investigation results."
        )

    reason = payload.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        reason = "Account locked due to investigation exceeding risk threshold."

    normalized: dict[str, Any] = {
        "action": "lock_account",
        "account_id": account_id,
        "reason": reason.strip(),
    }
    if ext_user_id:
        normalized["ext_user_id"] = ext_user_id
    if case_file is not None:
        normalized["case_file"] = case_file

    return normalized, None


async def _delegate_via_a2a(
    *,
    agent_label: str,
    cache_key: str,
    service_url: str,
    payload_prefix: str,
    payload: Any,
) -> dict[str, Any]:
    """Send a JSON-RPC message to a downstream agent and return normalized output."""
    client = _get_or_create_client(cache_key, service_url)
    if client is None:
        return {"agent": agent_label, "error": f"Unable to connect to {agent_label}"}

    payload_json = _normalize_payload(payload, agent_label)
    if payload_json is None:
        return {
            "agent": agent_label,
            "error": "Provided payload is not valid JSON",
        }

    message = Message(
        message_id=str(uuid.uuid4()),
        role=Role.user,
        parts=[TextPart(text=f"{payload_prefix} {payload_json}")],
    )
    request = SendMessageRequest(
        id=str(uuid.uuid4()),
        params=MessageSendParams(message=message),
    )

    try:
        response = await client.send_message(request)
