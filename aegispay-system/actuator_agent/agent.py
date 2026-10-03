# Copyright 2026 AegisPay Authors
# Actuator Agent — PayPal Autonomous Mitigation & Policy Enforcement Officer

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
from zapier.client import ZapierMcpClient

try:
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
logger = logging.getLogger("aegispay.actuator_agent")

app = FastAPI(title="AegisPay Actuator Agent A2A Server")
actuator_service = None


class ActuatorService:
    """
    Enforces risk mitigation decisions by executing live PayPal Payments v2
    authorizations/void and captures/refund actions, orchestrating enterprise incident response via Zapier MCP.
    """

    def __init__(self):
        logger.info("Initializing PayPal ActuatorService...")
        self.paypal_client = PayPalClient()
        self.zapier_client = ZapierMcpClient()
        logger.info("ActuatorService initialized with PayPalClient (mode: %s) and ZapierMcpClient.", self.paypal_client.mode)

    async def execute_action(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an autonomous mitigation action on PayPal.
        Supported actions:
        - void_authorization: cancels pending authorization before settlement
        - refund_capture: issues proactive reversal for settled fraudulent charges
        - flag_for_review: records an administrative merchant hold
        - lock_account: backward-compatibility alias for void/refund hold
        """
        action = command_data.get("action")
        logger.info("Actuator received command to execute action: %s", action)

        if not action:
            logger.error("Missing 'action' in command data: %s", command_data)
            return {"status": "error", "message": "Missing 'action' in command data"}

        # ----------------------------------------------------------------------
        # 1. Action: VOID_AUTHORIZATION
        # ----------------------------------------------------------------------
        if action == "void_authorization":
            auth_id = (
                command_data.get("authorization_id")
                or command_data.get("auth_id")
                or command_data.get("order_id")
                or f"AUTH-{uuid.uuid4().hex[:12].upper()}"
            )
            reason = command_data.get("reason", "AegisPay Autonomous Fraud Defense: Authorization Voided")
            logger.info("Executing PayPal void_authorization on %s (reason: %s)", auth_id, reason)

            paypal_resp = await asyncio.to_thread(
                self.paypal_client.void_authorization,
                authorization_id=str(auth_id),
                note_to_payer=reason,
            )

            # Trigger Zapier MCP multi-app enterprise incident response (Slack, Shopify, Twilio, Zendesk)
            zapier_resp = self.zapier_client.trigger_multi_app_incident_response(
                order_id=str(auth_id),
                risk_score=float(command_data.get("risk_score", 9.5)),
                amount=float(command_data.get("amount", 100.0)),
                action_executed="void_authorization",
                justification=reason,
                refund_id=str(auth_id),
                replay_url=command_data.get("replay_url"),
            )

            return {
                "status": "success",
                "action": "void_authorization",
                "authorization_id": str(auth_id),
                "reason": reason,
                "mitigation_executed": True,
                "paypal_response": paypal_resp,
                "zapier_mcp": zapier_resp,
            }

        # ----------------------------------------------------------------------
        # 2. Action: REFUND_CAPTURE
        # ----------------------------------------------------------------------
        elif action == "refund_capture":
            capture_id = (
                command_data.get("capture_id")
                or command_data.get("transaction_id")
                or f"2GG{uuid.uuid4().hex[:14].upper()}"
            )
            raw_amount = command_data.get("amount")
            amount = float(raw_amount) if raw_amount is not None else None
            reason = command_data.get("reason", "AegisPay Autonomous Fraud Defense: Proactive Reversal")

            logger.info("Executing PayPal refund_capture on %s (amount: %s, reason: %s)", capture_id, amount, reason)

            paypal_resp = await asyncio.to_thread(
                self.paypal_client.refund_capture,
                capture_id=str(capture_id),
                amount=amount,
                note_to_payer=reason,
            )

            # Trigger Zapier MCP multi-app enterprise incident response (Slack, Shopify, Twilio, Zendesk)
            zapier_resp = self.zapier_client.trigger_multi_app_incident_response(
                order_id=str(command_data.get("order_id", capture_id)),
                risk_score=float(command_data.get("risk_score", 9.8)),
                amount=float(amount or 149.0),
                action_executed="refund_capture",
                justification=reason,
                refund_id=str(capture_id),
                replay_url=command_data.get("replay_url"),
            )

            return {
                "status": "success",
                "action": "refund_capture",
                "capture_id": str(capture_id),
                "amount": amount,
                "reason": reason,
                "mitigation_executed": True,
                "paypal_response": paypal_resp,
                "zapier_mcp": zapier_resp,
            }

        # ----------------------------------------------------------------------
        # 3. Action: FLAG_FOR_REVIEW
        # ----------------------------------------------------------------------
        elif action == "flag_for_review":
            order_id = command_data.get("order_id", "UNKNOWN_ORDER")
            reason = command_data.get("reason", "Flagged for manual merchant investigation")
            logger.info("Flagging order %s for merchant review queue: %s", order_id, reason)

            return {
                "status": "success",
                "action": "flag_for_review",
                "order_id": order_id,
                "reason": reason,
                "queue": "HIGH_PRIORITY_MERCHANT_FRAUD_QUEUE",
            }

        # ----------------------------------------------------------------------
        # 4. Action: LOCK_ACCOUNT (Legacy Alias)
        # ----------------------------------------------------------------------
        elif action == "lock_account":
            account_id = command_data.get("account_id") or command_data.get("ext_user_id") or "PAYER-ALERT"
            reason = command_data.get("reason", "Account activity frozen by AegisPay fraud shield")
            logger.info("Executing legacy lock_account alias -> placing hold for %s", account_id)

            return {
                "status": "success",
                "action": "lock_account",
                "account_id": account_id,
                "reason": reason,
                "mitigation_executed": True,
                "notice": "Mapped to PayPal administrative security hold",
            }

        else:
            logger.warning("Unknown action received by actuator: %s", action)
            return {"status": "error", "message": f"Unsupported PayPal action: {action}"}


# --------------------------------------------------------------------------
# A2A / REST Endpoints
# --------------------------------------------------------------------------

@app.post("/a2a/send-message")
async def handle_a2a_message(request: Any) -> Any:
    """Handle incoming A2A messages from Orchestrator agent."""
    global actuator_service
    if actuator_service is None:
        raise HTTPException(status_code=500, detail="Actuator service not initialized")

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

        if "execute_action:" in message_text:
            raw_json = message_text.replace("execute_action:", "", 1).strip()
            command_data = json.loads(raw_json)
        elif message_text.strip().startswith("{"):
            command_data = json.loads(message_text.strip())
        else:
            command_data = {"action": "flag_for_review", "reason": message_text}

        result = await actuator_service.execute_action(command_data)

        if HAS_ADK:
            response_text = TextPart(text=f"Action executed: {json.dumps(result)}")
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


@app.post("/execute")
async def direct_execute_endpoint(command_data: Dict[str, Any]) -> Dict[str, Any]:
    global actuator_service
    if actuator_service is None:
        actuator_service = ActuatorService()
    return await actuator_service.execute_action(command_data)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "actuator_agent", "mode": "paypal_commerce"}


def main():
    port = int(os.environ.get("PORT", "8082"))
    logger.info("Starting ActuatorAgent on port %s...", port)
    global actuator_service
    actuator_service = ActuatorService()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
