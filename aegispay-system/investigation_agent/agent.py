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
                else:
                    logger.warning(f"Unexpected response format from genai-toolbox: {result}")
                    return []
            else:
                result = response.json() if response.headers.get('content-type') == 'application/json' else {}
                if "error" in result:
                    logger.error(f"genai-toolbox API error: {result['error']}")
                    return []
                else:
                    logger.error(f"genai-toolbox HTTP error: {response.status_code} - {response.text}")
                    return []
        except Exception as e:
            logger.error(f"Error calling genai-toolbox API: {e}")
            return []

    async def investigate_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives a transaction, gathers context, uses an LLM to analyze it,
        and returns a structured case file.
        """
        logger.info(f"Received request to investigate transaction: {transaction_data.get('transaction_id')}")
        account_id = transaction_data.get("from_account_id")
        if not account_id:
            logger.error("Missing 'from_account_id' in transaction data.")
            return {"error": "Missing from_account_id in transaction data"}

        try:
            logger.info(f"Fetching details for account: {account_id}")
            # Use REST API calls to genai-toolbox
            user_details = await asyncio.to_thread(
                self.call_genai_toolbox_api,
                "get_user_details_by_account",
                {"account_id": account_id}
            )
            logger.info(f"Fetching transaction history for account: {account_id}")
            transaction_history = await asyncio.to_thread(
                self.call_genai_toolbox_api,
                "get_user_transaction_history",
                {"account_id": account_id}
            )
        except Exception as e:
            logger.error(f"Error calling GenAI Toolbox: {e}", exc_info=True)
            return {"error": f"Failed to gather context: {e}"}

        prompt = (
            "Please investigate the following transaction:\n"
            f"{json.dumps(transaction_data, indent=2)}\n\n"
            "Here is the user's profile:\n"
            f"{json.dumps(user_details, indent=2)}\n\n"
            "And here is the user's recent transaction history:\n"
            f"{json.dumps(transaction_history, indent=2)}\n\n"
            "Provide your risk assessment as a JSON object."
        )

        try:
            logger.info("Sending data to LLM for fraud analysis...")
            message_content = types.Content(
                role="user",
                parts=[types.Part(text=prompt)],
            )

            user_id = transaction_data.get("from_account_id") or self.default_user_id
            session_id = str(uuid.uuid4())
            await self.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=session_id,
            )

            final_text = ""
            last_text = ""

            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message_content,
            ):
                if getattr(event, "content", None) and getattr(event.content, "parts", None):
                    text_segments = []
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            text_segments.append(part.text.strip())
                    if text_segments:
                        last_text = "\n".join(filter(None, text_segments))

                if getattr(event, "is_final_response", None) and event.is_final_response():
                    final_text = last_text

            llm_response = final_text or last_text
            if not llm_response:
                raise ValueError("Received empty response from investigation LLM")

            cleaned_response = (
                llm_response.strip()
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            analysis = json.loads(cleaned_response)
            logger.info(f"Received analysis from LLM: {analysis}")
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}", exc_info=True)
            return {"error": f"Failed to get analysis from LLM: {e}", "llm_response": str(e)}

        case_file = {
            "transaction_data": transaction_data,
            "user_details": user_details,
            "transaction_history": transaction_history,
            "fraud_analysis": analysis,
        }
        logger.info(f"Case file created for transaction: {transaction_data.get('transaction_id')}")
        return case_file


# A2A FastAPI endpoints
@app.post("/a2a/send-message")
async def handle_a2a_message(request: SendMessageRequest) -> SendMessageResponse:
    """Handle incoming A2A messages from other agents."""
    global investigation_service
    
