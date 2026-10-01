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
import asyncio
from typing import Dict, Any, Optional

import requests
from fastapi import FastAPI, HTTPException
import uvicorn
from a2a.types import (
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Message,
    TextPart,
    Role,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get config from environment variables
GENAL_TOOLBOX_URL = os.environ.get("GENAL_TOOLBOX_SERVICE_URL", "http://genal-toolbox-service")

# Create FastAPI app for A2A server functionality
app = FastAPI(title="Actuator Agent A2A Server")

# Global actuator service instance
actuator_service = None


def _strip_str(value: Any) -> Optional[str]:
    if isinstance(value, str):
        candidate = value.strip()
        if candidate:
            return candidate
    return None


def _extract_account_id(payload: Dict[str, Any]) -> Optional[str]:
    account_id = _strip_str(payload.get("account_id"))
    if account_id:
        return account_id

    case_file = payload.get("case_file")
    if isinstance(case_file, dict):
        transaction_data = case_file.get("transaction_data")
        if isinstance(transaction_data, dict):
            for key in ("account_id", "from_account_id", "user_id"):
                candidate = _strip_str(transaction_data.get(key))
                if candidate:
                    return candidate

        user_details = case_file.get("user_details")
        if isinstance(user_details, dict):
            for key in ("account_id", "ext_user_id"):
                candidate = _strip_str(user_details.get(key))
                if candidate:
                    return candidate
        elif isinstance(user_details, list):
            for entry in user_details:
                if isinstance(entry, dict):
                    for key in ("account_id", "ext_user_id"):
                        candidate = _strip_str(entry.get(key))
                        if candidate:
                            return candidate

    ext_user_id = _strip_str(payload.get("ext_user_id"))
    if ext_user_id:
        return ext_user_id

    return None


class ActuatorService:
    def __init__(self):
        logger.info("Initializing ActuatorService...")
        self.genal_toolbox_url = GENAL_TOOLBOX_URL
        logger.info("ActuatorService initialized.")

    def call_genai_toolbox_api(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a GenAI Toolbox tool via its REST API."""
        url = f"{self.genal_toolbox_url}/api/tool/{tool_name}/invoke"
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict):
                    if "data" in result:
                        data = result["data"]
                    elif "rows" in result:
                        data = result["rows"]
                    elif "result" in result:
                        data = result["result"]
                    else:
                        data = result

                    if isinstance(data, str):
