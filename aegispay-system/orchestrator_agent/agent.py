# Copyright 2026 AegisPay Authors
# Orchestrator Agent — Command & Decision Swarm Leader for PayPal Commerce

import os
import sys
import logging
import json
import uuid
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import httpx
# Ensure aegispay-system packages are reachable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from paypal import PayPalClient
from elasticsearch.client import ElasticThreatIntelClient
from kernel import KernelBrowserClient
from zapier import ZapierMcpClient

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
logger = logging.getLogger("aegispay.orchestrator_agent")

# Configuration from environment
INVESTIGATION_URL = os.environ.get("INVESTIGATION_AGENT_SERVICE_URL", "http://localhost:8081")
ACTUATOR_URL = os.environ.get("ACTUATOR_AGENT_SERVICE_URL", "http://localhost:8082")
RISK_SCORE_THRESHOLD = float(os.environ.get("RISK_SCORE_THRESHOLD", "7.0"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ORCHESTRATOR_DOCTRINE = """
You are AegisPay Orchestrator, the central command agent defending PayPal commerce merchants against fraud.
1. Always delegate incoming PayPal transactions to InvestigationAgent to produce an evidence-backed case file and risk score (0-10).
2. If risk_score >= {threshold}:
   - If payment is captured: invoke ActuatorAgent with action "refund_capture".
   - If payment is authorized or pending: invoke ActuatorAgent with action "void_authorization".
3. If risk_score < {threshold}:
   - Approve transaction with zero defensive friction.
4. Conclude with a transparent audit summary.
"""

app = FastAPI(title="AegisPay Orchestrator Command Agent")

# Allow CORS for AG Grid Dashboard on port 8088 or any local dev port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator_service = None
_sse_subscribers: List[asyncio.Queue] = []


class OrchestratorService:
    def __init__(self):
        logger.info("Initializing PayPal OrchestratorService (threshold: %s)...", RISK_SCORE_THRESHOLD)
        self.risk_threshold = RISK_SCORE_THRESHOLD
        self.paypal_client = PayPalClient()
        self.investigation_url = INVESTIGATION_URL
        self.actuator_url = ACTUATOR_URL
        self.elastic_client = ElasticThreatIntelClient()
        self.kernel_client = KernelBrowserClient()
        self.zapier_client = ZapierMcpClient()
        self._http_client = httpx.AsyncClient(timeout=25.0)

    async def broadcast_event(self, event_data: Dict[str, Any]):
        """Broadcast live investigation and mitigation events to all dashboard SSE listeners."""
        for queue in list(_sse_subscribers):
            try:
                await queue.put(event_data)
            except Exception:
                _sse_subscribers.remove(queue)

    async def process_transaction_alert(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinates the multi-agent fraud investigation and autonomous mitigation pipeline.
        1. Calls InvestigationAgent
        2. Evaluates risk score against threshold
        3. Calls ActuatorAgent if mitigation is warranted
        4. Broadcasts live trace to Ops Dashboard
        """
        session_id = str(uuid.uuid4())
        order_id = (
            transaction_data.get("order_id")
            or transaction_data.get("id")
            or transaction_data.get("transaction_id")
            or f"5O{uuid.uuid4().hex[:14].upper()}"
        )
        logger.info("Orchestrator processing transaction alert for order %s (session %s)", order_id, session_id)

        tool_events: List[Dict[str, Any]] = []

        # ----------------------------------------------------------------------
        # Step 1: Delegate to InvestigationAgent
        # ----------------------------------------------------------------------
        tool_events.append({"event": "call", "tool": "InvestigationAgent", "args": {"order_id": order_id}})
        investigation_result: Optional[Dict[str, Any]] = None

        try:
            # Try HTTP call to InvestigationAgent service
            resp = await self._http_client.post(
                f"{self.investigation_url}/investigate",
                json=transaction_data,
                timeout=15.0,
            )
            if resp.status_code == 200:
                investigation_result = resp.json()
            else:
                logger.warning("Investigation service returned %s, using internal fallback", resp.status_code)
        except Exception as e:
            logger.info("Downstream investigation agent offline or direct invocation: %s", e)

        # Fallback to local InvestigationService if standalone or in same process
        if not investigation_result:
            from investigation_agent.agent import InvestigationService
            local_inv = InvestigationService()
            investigation_result = await local_inv.investigate_transaction(transaction_data)

        tool_events.append({"event": "response", "tool": "InvestigationAgent", "response": investigation_result})

        # Extract risk metrics
        fraud_analysis = investigation_result.get("fraud_analysis", {})
        risk_score = float(fraud_analysis.get("risk_score", 0.0))
        risk_level = fraud_analysis.get("risk_level", "LOW")
        signals = fraud_analysis.get("signals", [])
        recommended_action = fraud_analysis.get("recommended_action", "APPROVE")
        justification = fraud_analysis.get("justification", "Standard checkout")

        # ----------------------------------------------------------------------
        # Step 2: Policy Threshold Evaluation & Actuator Delegation
        # ----------------------------------------------------------------------
        should_actuate = risk_score >= self.risk_threshold
        actuator_result: Optional[Dict[str, Any]] = None

        if should_actuate:
            intent = transaction_data.get("intent", "CAPTURE")
            status = transaction_data.get("status", "APPROVED")

            # Determine appropriate PayPal Payments v2 API action
            if intent == "AUTHORIZE" or status == "AUTHORIZED":
                actuator_payload = {
                    "action": "void_authorization",
                    "authorization_id": order_id,
                    "order_id": order_id,
                    "reason": f"AegisPay Autonomous Defense: Risk score {risk_score:.1f}/10 exceeded threshold ({self.risk_threshold})",
                }
            else:
                raw_amt = (
                    transaction_data.get("purchase_units", [{}])[0].get("amount", {}).get("value")
                    or transaction_data.get("amount")
                    or 0.0
                )
                actuator_payload = {
                    "action": "refund_capture",
                    "capture_id": f"2GG{order_id[2:] if len(order_id) > 2 else 'PAYPAL'}",
                    "amount": float(raw_amt),
                    "reason": f"AegisPay Autonomous Defense: Proactive reversal for {', '.join(signals[:1]) if signals else 'High risk'}",
                }

            tool_events.append({"event": "call", "tool": "ActuatorAgent", "args": actuator_payload})

            try:
                act_resp = await self._http_client.post(
                    f"{self.actuator_url}/execute",
                    json=actuator_payload,
                    timeout=15.0,
                )
                if act_resp.status_code == 200:
                    actuator_result = act_resp.json()
            except Exception as e:
                logger.info("Downstream actuator agent offline or direct invocation: %s", e)

            # Local fallback if standalone
            if not actuator_result:
                from actuator_agent.agent import ActuatorService
                local_act = ActuatorService()
                actuator_result = await local_act.execute_action(actuator_payload)

            tool_events.append({"event": "response", "tool": "ActuatorAgent", "response": actuator_result})
            summary = (
                f"[ESCALATED] Order {order_id} flagged with risk score {risk_score:.1f}/10 ({risk_level}). "
                f"Autonomous mitigation triggered: executed {actuator_payload['action']} via PayPal API. {justification}"
            )
        else:
            summary = (
                f"[APPROVED] Order {order_id} cleared with risk score {risk_score:.1f}/10 ({risk_level}). "
                f"Within safe operating threshold ({self.risk_threshold}). No mitigation required."
            )

        risk_signals_ctx = investigation_result.get("risk_signals", {}) if investigation_result else {}
        ip_country = risk_signals_ctx.get("shipping_country") or risk_signals_ctx.get("payer_country") or "US"
        capture_id = None
        if actuator_result:
            capture_id = actuator_result.get("capture_id") or actuator_result.get("authorization_id")

        final_record = {
            "session_id": session_id,
            "order_id": order_id,
            "timestamp": transaction_data.get("create_time") or transaction_data.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "ip_country": ip_country,
            "capture_id": capture_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "should_actuate": should_actuate,
            "recommended_action": recommended_action,
            "signals": signals,
            "justification": justification,
            "summary": summary,
            "transaction_data": transaction_data,
            "investigation_result": investigation_result,
            "actuator_result": actuator_result,
            "tool_events": tool_events,
        }

        # Index transaction asynchronously into Elasticsearch
        try:
            self.elastic_client.index_transaction(final_record)
        except Exception as e:
            logger.debug("Non-blocking Elastic indexing error: %s", e)

        # Broadcast live to connected AG Grid dashboards
        await self.broadcast_event(final_record)
        return final_record


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------

@app.post("/api/elastic/esql")
async def execute_esql_endpoint(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """Executes live ES|QL (Elasticsearch Query Language) query against Elastic Cloud Serverless."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    query_str = request_body.get("query", "FROM aegispay_threat_intel | LIMIT 5")
    return orchestrator_service.elastic_client.run_esql(query_str)


@app.get("/api/kernel/health")
async def kernel_health_endpoint() -> Dict[str, Any]:
    """Returns KERNEL cloud browser infrastructure health status and capabilities."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    return orchestrator_service.kernel_client.health_check()


@app.post("/api/kernel/audit-checkout")
async def kernel_audit_checkout_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Triggers an autonomous 'Mystery Shopper' DOM storefront audit via Kernel cloud browser (<30ms spinup)."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    store_url = payload.get("store_url", "https://store.apple-authorized-merchant.com/checkout")
    product_name = payload.get("product_name", "Apple MacBook Pro 16")
    checkout_amount = float(payload.get("checkout_amount", 149.00))
    channel3_fmv = float(payload.get("channel3_fmv", 3499.00))
    return orchestrator_service.kernel_client.audit_merchant_checkout_dom(
        store_url=store_url,
        product_name=product_name,
        checkout_amount=checkout_amount,
        channel3_fmv=channel3_fmv
    )


@app.post("/api/kernel/verify-tracking")
async def kernel_verify_tracking_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Autonomous dispute carrier evidence harvester via Kernel stealth browser."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    carrier = payload.get("carrier", "FedEx")
    tracking_number = payload.get("tracking_number", "794829104928")
    return orchestrator_service.kernel_client.verify_carrier_dispute_evidence(carrier, tracking_number)


@app.get("/api/zapier/health")
async def zapier_health_endpoint() -> Dict[str, Any]:
    """Returns Zapier MCP multi-app gateway health status and active integrations."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    return orchestrator_service.zapier_client.health_check()


@app.get("/api/zapier/tools")
async def zapier_tools_endpoint() -> Dict[str, Any]:
    """Lists all available Model Context Protocol (MCP) tools exposed by Zapier."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    return {"tools": orchestrator_service.zapier_client.list_available_tools()}


@app.post("/api/zapier/trigger-incident")
async def zapier_trigger_incident_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Triggers an autonomous 4-app enterprise incident response via Zapier MCP."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    return orchestrator_service.zapier_client.trigger_multi_app_incident_response(
        order_id=payload.get("order_id", "5O11016942TN401931"),
        risk_score=float(payload.get("risk_score", 9.8)),
        amount=float(payload.get("amount", 3499.00)),
        action_executed=payload.get("action_executed", "refund_capture"),
        justification=payload.get("justification", "AegisPay Autonomous Defense: Proactive fraud reversal"),
        refund_id=payload.get("refund_id"),
        replay_url=payload.get("replay_url"),
    )


@app.post("/process-transaction")
async def process_transaction_endpoint(transaction: Dict[str, Any]) -> Dict[str, Any]:
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()
    return await orchestrator_service.process_transaction_alert(transaction)


@app.post("/simulate-scenario/{scenario_name}")
async def simulate_scenario_endpoint(scenario_name: str) -> Dict[str, Any]:
    """Generates a scenario (ACCOUNT_TAKEOVER, CARD_TESTING_BOT, PRICE_TAMPERING, etc.) and routes it."""
    global orchestrator_service
    if orchestrator_service is None:
        orchestrator_service = OrchestratorService()

    if scenario_name.lower() in ("price_tampering", "cart_tampering"):
        order = {
            "id": f"5O{uuid.uuid4().hex[:14].upper()}",
            "intent": "CAPTURE",
            "status": "APPROVED",
            "payer": {
                "payer_id": f"PAYER-{uuid.uuid4().hex[:8].upper()}",
                "name": {"given_name": "TamperBot", "surname": "Session_X"},
                "email_address": "exploit_user@darknet-market.org",
            },
            "purchase_units": [
                {
                    "reference_id": "PU-TAMPER-01",
                    "amount": {"currency_code": "USD", "value": "149.00"},
                    "description": "Exploit: $3,499 MacBook cart price slashed to $149",
                    "items": [
                        {
                            "name": "Apple MacBook Pro 16",
                            "unit_amount": {"currency_code": "USD", "value": "149.00"},
                            "quantity": "1",
                            "category": "PHYSICAL_GOODS",
                        }
                    ],
                    "shipping": {
                        "address": {"admin_area_2": "Miami", "country_code": "US"}
                    },
                }
            ],
            "create_time": "2026-10-03T03:30:00Z",
        }
        return await orchestrator_service.process_transaction_alert(order)

    from paypal import FraudScenario
    try:
        scenario = FraudScenario(scenario_name.upper())
    except ValueError:
        scenario = FraudScenario.ACCOUNT_TAKEOVER

    order = orchestrator_service.paypal_client.simulator.generate_simulated_order(scenario)
    return await orchestrator_service.process_transaction_alert(order)


@app.get("/events/stream")
async def event_stream(request: Request):
    """Server-Sent Events endpoint streaming real-time fraud alerts to AG Grid Dashboard."""
    queue = asyncio.Queue()
    _sse_subscribers.append(queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in _sse_subscribers:
                _sse_subscribers.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchestrator_agent", "mode": "paypal_commerce"}


def main():
    port = int(os.environ.get("PORT", "8085"))
    logger.info("Starting OrchestratorAgent on port %s...", port)
    global orchestrator_service
    orchestrator_service = OrchestratorService()
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
