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
import requests
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
import uvicorn
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from a2a.types import SendMessageRequest, SendMessageResponse, SendMessageSuccessResponse, Message, TextPart, Role

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get config from environment variables
GENAL_TOOLBOX_URL = os.environ.get("GENAL_TOOLBOX_SERVICE_URL", "http://genal-toolbox-service")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

INVESTIGATION_PROMPT = """
You are a financial investigator. Your task is to analyze the provided transaction and user data to assess the risk of fraud.
Based on the information, provide a risk score from 0 (no risk) to 10 (high risk) and a detailed justification for your assessment.
Consider the transaction amount, user's transaction history, and any other relevant details.
Format your response as a JSON object with two keys: "risk_score" and "justification".
"""

# Create FastAPI app for A2A server functionality
app = FastAPI(title="Investigation Agent A2A Server")

# Global investigation service instance
investigation_service = None

class InvestigationService:
    def __init__(self):
        logger.info("Initializing InvestigationService...")
        self.genal_toolbox_url = GENAL_TOOLBOX_URL
        self.llm_agent = LlmAgent(
            name="investigation_agent",
            model=Gemini(api_key=GEMINI_API_KEY, model="gemini-2.5-flash"),
            instruction=INVESTIGATION_PROMPT,
        )
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name="investigation_agent_app",
            agent=self.llm_agent,
            session_service=self.session_service,
        )
        self.default_user_id = "orchestrator"
        logger.info("InvestigationService initialized.")

    def call_genai_toolbox_api(self, tool_name: str, payload: dict):
        """Helper method to call genai-toolbox REST API."""
        try:
            url = f"{self.genal_toolbox_url}/api/tool/{tool_name}/invoke"
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Extract data from various possible response formats
                if isinstance(result, dict):
                    if "data" in result:
                        data = result["data"]
                    elif "rows" in result:
                        data = result["rows"]
                    elif "result" in result:
                        data = result["result"]
                    else:
                        data = result if isinstance(result, list) else []
                    
                    # If data is a string, parse it as JSON
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON response from genai-toolbox: {e}")
                            return []
                    
                    return data if isinstance(data, list) else [data] if data else []
                elif isinstance(result, list):
                    return result
