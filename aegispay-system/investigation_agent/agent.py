# Copyright 2026 AegisPay Authors
# Investigation Agent — PayPal Commerce Fraud Detective & Context Reasoner

import os
import sys
import logging
import json
import uuid
import asyncio
from typing import Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
import uvicorn

# Ensure paypal client module is reachable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from paypal import PayPalClient
from channel3 import Channel3Client

try:
    from google.adk.agents import LlmAgent
    from google.adk.models import Gemini
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.adk.runners import Runner
    from google.genai import types
    from a2a.types import (
        SendMessageRequest,
        SendMessageResponse,
        SendMessageSuccessResponse,
        Message,
        TextPart,
        Role,
    )
    HAS_ADK = True
except ImportError:
    HAS_ADK = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("aegispay.investigation_agent")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

PAYPAL_INVESTIGATION_PROMPT = """
You are AegisPay Investigation Agent, an expert in PayPal merchant fraud defense grounded in APIMatic API context.
Your task is to analyze the provided PayPal checkout order, buyer telemetry, shipping destination, dispute records, and risk signals.

Assess the risk of:
1. Account Takeover (ATO) or credential stuffing (e.g., dormant account suddenly buying high-value goods).
2. Card Testing Bots or velocity anomalies (e.g., rapid micro-transactions, burner email domains).
3. Cross-border freight forwarding / shipping address mismatch.
4. Friendly fraud or serial chargeback exploit schemes.

Respond strictly in valid JSON format with these exact keys:
{
  "risk_score": <float between 0.0 and 10.0>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "recommended_action": "<APPROVE|FLAG_FOR_REVIEW|VOID_AUTHORIZATION|REFUND_CAPTURE>",
  "signals": ["<SIGNAL_1>", "<SIGNAL_2>"],
  "justification": "<concise 2-sentence rationale citing specific evidence>"
}
"""

app = FastAPI(title="AegisPay Investigation Agent A2A Server")
investigation_service = None


class InvestigationService:
    def __init__(self):
        logger.info("Initializing PayPal InvestigationService...")
        self.paypal_client = PayPalClient()
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.has_llm = bool(
            HAS_ADK
            and self.gemini_api_key
            and not self.gemini_api_key.startswith("your_")
            and len(self.gemini_api_key) > 15
        )

        self.channel3_client = Channel3Client()

        if self.has_llm:
            try:
                self.llm_agent = LlmAgent(
                    name="investigation_agent",
                    model=Gemini(api_key=self.gemini_api_key, model="gemini-2.5-flash"),
                    instruction=PAYPAL_INVESTIGATION_PROMPT,
                )
                self.session_service = InMemorySessionService()
                self.runner = Runner(
                    app_name="investigation_agent_app",
                    agent=self.llm_agent,
                    session_service=self.session_service,
                )
                self.default_user_id = "orchestrator"
                logger.info("Gemini 2.5 Flash Investigation runner initialized.")
            except Exception as e:
                logger.warning("Could not initialize ADK LLM runner: %s. Using deterministic risk engine.", e)
                self.has_llm = False
        else:
            logger.info("Running InvestigationService with APIMatic-grounded heuristic risk engine.")

    async def investigate_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives a PayPal transaction or order, gathers PayPal API context,
        evaluates risk signals, and returns a structured fraud case file.
        """
        order_id = (
            transaction_data.get("order_id")
            or transaction_data.get("id")
            or transaction_data.get("transaction_id")
        )
        logger.info("Investigating PayPal transaction / order: %s", order_id)

        # 1. Gather PayPal Order Context
        order_details = transaction_data
        if order_id and ("purchase_units" not in transaction_data):
            try:
                order_details = self.paypal_client.get_order_details(str(order_id))
            except Exception as err:
                logger.warning("Error fetching order details from PayPal: %s", err)
                order_details = transaction_data

        # 2. Extract Objective PayPal Risk Signals (APIMatic Grounded)
        risk_signals = self.paypal_client.extract_risk_signals(order_details)
        disputes = self.paypal_client.list_disputes()

        # 3. Channel3 Product Intelligence & Fair Market Value (FMV) Verification
        items = order_details.get("purchase_units", [{}])[0].get("items", [])
        item_name = items[0].get("name") if items else transaction_data.get("category", "Retail Merchandise")
        amount = risk_signals.get("amount_usd", 0.0)
        channel3_fmv = self.channel3_client.verify_fair_market_value(item_name, amount)

        if channel3_fmv.get("is_tampered"):
            tamper_msg = (
                f"CHANNEL3_PRICE_TAMPERING: Cart price (${amount:.2f}) deviates by {channel3_fmv['variance_pct']}% "
                f"from Channel3 Fair Market Value (${channel3_fmv['market_price']:.2f} for '{channel3_fmv['verified_title']}')"
            )
            risk_signals.setdefault("signals_detected", []).append(tamper_msg)

        # 4. LLM or Heuristic Reasoning
        analysis: Dict[str, Any] = {}
        if self.has_llm:
            prompt = (
                "Please investigate this PayPal transaction for fraud:\n"
                f"Order Details:\n{json.dumps(order_details, indent=2)}\n\n"
                f"Extracted Risk Signals:\n{json.dumps(risk_signals, indent=2)}\n\n"
                f"Channel3 Product Data:\n{json.dumps(channel3_fmv, indent=2)}\n\n"
                f"Recent Disputes Context:\n{json.dumps(disputes, indent=2)}\n\n"
                "Provide your risk assessment as JSON."
            )
            try:
                message_content = types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                )
                user_id = "orchestrator"
                session_id = str(uuid.uuid4())
                await self.session_service.create_session(
                    app_name=self.runner.app_name,
                    user_id=user_id,
                    session_id=session_id,
                )
                final_text = ""
                async for event in self.runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=message_content,
                ):
                    if getattr(event, "content", None) and getattr(event.content, "parts", None):
                        text_parts = [p.text for p in event.content.parts if getattr(p, "text", None)]
                        if text_parts:
                            final_text = "\n".join(text_parts)

                cleaned = final_text.strip().replace("```json", "").replace("```", "").strip()
                analysis = json.loads(cleaned)
                logger.info("Gemini 2.5 Flash investigation completed for %s: %s", order_id, analysis)
            except Exception as e:
                logger.warning("LLM reasoning fallback: %s", e)
                analysis = self._compute_heuristic_analysis(order_details, risk_signals, channel3_fmv)
        else:
            analysis = self._compute_heuristic_analysis(order_details, risk_signals, channel3_fmv)

        case_file = {
            "order_id": order_id,
            "transaction_data": transaction_data,
            "paypal_order_details": order_details,
            "risk_signals": risk_signals,
            "disputes_context": disputes,
            "channel3_product_data": channel3_fmv,
            "fraud_analysis": analysis,
        }
        return case_file

    def _compute_heuristic_analysis(
        self, order_details: Dict[str, Any], risk_signals: Dict[str, Any], channel3_fmv: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """APIMatic-grounded & Channel3-verified deterministic risk reasoning."""
        signals = risk_signals.get("signals_detected", [])
        amount = risk_signals.get("amount_usd", 0.0)
        sig_count = len(signals)

        # High priority check: Channel3 Price Tampering
        if channel3_fmv and channel3_fmv.get("is_tampered"):
            score = 9.8
            level = "CRITICAL"
            action = "REFUND_CAPTURE" if order_details.get("intent") == "CAPTURE" else "VOID_AUTHORIZATION"
            justification = (
                f"Channel3 Product Intelligence Alert: Cart Price Tampering detected! "
                f"Order charged ${amount:.2f} for '{channel3_fmv.get('verified_title')}' (Verified Market Value: "
                f"${channel3_fmv.get('market_price'):.2f}, Variance: {channel3_fmv.get('variance_pct')}%). "
                f"Immediate PayPal Payments v2 {action.lower()} executed."
            )
        elif sig_count >= 2 or amount >= 3000.0:
            score = 9.4
            level = "CRITICAL"
            action = "REFUND_CAPTURE" if order_details.get("intent") == "CAPTURE" else "VOID_AUTHORIZATION"
            justification = (
                f"Critical risk detected with {sig_count} severe anomaly indicators including "
                f"{', '.join(signals[:2])}. Immediate mitigation required to prevent chargeback."
            )
        elif sig_count == 1 or amount >= 1000.0:
            score = 7.8
            level = "HIGH"
            action = "VOID_AUTHORIZATION" if order_details.get("intent") == "AUTHORIZE" else "FLAG_FOR_REVIEW"
            justification = (
                f"High risk transaction exceeding monitoring threshold: {signals[0] if signals else 'High ticket amount'}. "
                "Autonomous payment mitigation or manual escalation advised."
            )
        else:
            score = 1.2
            level = "LOW"
            action = "APPROVE"
            justification = (
                "Verified commerce transaction with zero risk anomalies. Buyer tenure, billing address, "
                "and Channel3 Fair Market Value match PayPal Seller Protection criteria."
            )

        return {
            "risk_score": score,
            "risk_level": level,
            "recommended_action": action,
            "signals": signals,
            "justification": justification,
        }


# --------------------------------------------------------------------------
# A2A / REST Endpoints
# --------------------------------------------------------------------------

@app.post("/a2a/send-message")
async def handle_a2a_message(request: Any) -> Any:
    """Handle incoming A2A messages from Orchestrator agent."""
    global investigation_service
    if investigation_service is None:
        raise HTTPException(status_code=500, detail="Investigation service not initialized")

    try:
        message_text = ""
        if hasattr(request, "params") and request.params:
            if hasattr(request.params, "message") and request.params.message:
                if hasattr(request.params.message, "parts") and request.params.message.parts:
                    for part in request.params.message.parts:
                        if hasattr(part, "root") and hasattr(part.root, "text"):
                            message_text = part.root.text
                            break
                        elif hasattr(part, "text"):
                            message_text = part.text
                            break

        if "investigate_transaction:" in message_text:
            raw_json = message_text.replace("investigate_transaction:", "", 1).strip()
            data = json.loads(raw_json)
        elif message_text.strip().startswith("{"):
            data = json.loads(message_text.strip())
        else:
            data = {"raw_text": message_text}

        result = await investigation_service.investigate_transaction(data)

        if HAS_ADK:
            response_text = TextPart(text=f"Investigation completed: {json.dumps(result)}")
            response_message = Message(
                message_id=str(uuid.uuid4()),
                role=Role.agent,
                parts=[response_text],
            )
            success_response = SendMessageSuccessResponse(
                id=getattr(request, "id", str(uuid.uuid4())),
                result=response_message,
            )
            return SendMessageResponse(root=success_response)
        return {"result": result}

    except Exception as e:
        logger.error("Error processing A2A message: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/")
async def handle_root_a2a_message(request: Any) -> Any:
    return await handle_a2a_message(request)


@app.post("/investigate")
async def direct_investigate_endpoint(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    global investigation_service
    if investigation_service is None:
        investigation_service = InvestigationService()
    return await investigation_service.investigate_transaction(transaction_data)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "investigation_agent", "mode": "paypal_commerce"}


def main():
    port = int(os.environ.get("PORT", "8081"))
    logger.info("Starting InvestigationAgent on port %s...", port)
    global investigation_service
    investigation_service = InvestigationService()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
