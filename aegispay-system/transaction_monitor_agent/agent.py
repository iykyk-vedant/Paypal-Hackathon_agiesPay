# Copyright 2026 AegisPay Authors
# Transaction Monitor Agent — PayPal Webhook Listener & Stream Sentinel

import os
import sys
import time
import asyncio
from datetime import datetime, timezone
import logging
import json
import random
from typing import Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
import uvicorn
import httpx

# Ensure paypal client module is reachable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from paypal import PayPalClient, FraudScenario

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("aegispay.transaction_monitor_agent")

ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_SERVICE_URL", "http://localhost:8085")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 6))
FRAUD_THRESHOLD = float(os.environ.get("FRAUD_THRESHOLD", 1000.0))

app = FastAPI(title="AegisPay Transaction Monitor & Webhook Receiver")
monitor_agent = None


class TransactionMonitorAgent:
    """
    Continuous stream monitor and webhook gateway for PayPal Commerce events.
    Listens for live checkout approval and payment capture events,
    pre-screens risk signals, and dispatches to the Orchestrator agent.
    """

    def __init__(self):
        logger.info("Initializing TransactionMonitorAgent (poll interval: %ss, threshold: $%s)...", POLL_INTERVAL, FRAUD_THRESHOLD)
        self.orchestrator_url = ORCHESTRATOR_URL
        self.paypal_client = PayPalClient()
        self.poll_interval = POLL_INTERVAL
        self.fraud_threshold = FRAUD_THRESHOLD
        self._http_client = httpx.AsyncClient(timeout=30.0)
        self.is_monitoring = False
        self._monitor_task = None

    async def start_stream(self):
        """Start the background streaming sentinel."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self._monitor_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Transaction stream sentinel activated.")

    async def stop_stream(self):
        """Stop background streaming sentinel."""
        self.is_monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
        logger.info("Transaction stream sentinel deactivated.")

    async def _monitoring_loop(self):
        """Continuous background loop simulating live commerce transaction arrivals."""
        while self.is_monitoring:
            try:
                # 80% legitimate commerce, 20% random fraud attack pattern
                r = random.random()
                if r < 0.65:
                    scenario = FraudScenario.LEGITIMATE_ORDER
                elif r < 0.80:
                    scenario = FraudScenario.ACCOUNT_TAKEOVER
                elif r < 0.90:
                    scenario = FraudScenario.CARD_TESTING_BOT
                else:
                    scenario = FraudScenario.CHARGEBACK_EXPLOIT

                order = self.paypal_client.simulator.generate_simulated_order(scenario)
                webhook_event = self.paypal_client.simulator.generate_webhook_event(order)

                logger.info(
                    "Sentinel generated streaming event: %s ($%s, %s)",
                    order.get("id"),
                    order.get("purchase_units", [{}])[0].get("amount", {}).get("value"),
                    scenario.value,
                )

                await self.forward_to_orchestrator(order)
            except Exception as e:
                logger.error("Error in streaming sentinel loop: %s", e)

            await asyncio.sleep(self.poll_interval)

    async def forward_to_orchestrator(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a transaction or order alert to the Orchestrator Swarm Leader."""
        logger.info("Forwarding order %s to Orchestrator at %s", order_data.get("id"), self.orchestrator_url)
        try:
            resp = await self._http_client.post(
                f"{self.orchestrator_url}/process-transaction",
                json=order_data,
                timeout=20.0,
            )
            if resp.status_code == 200:
                result = resp.json()
                logger.info("Orchestrator completed processing for %s: %s", order_data.get("id"), result.get("summary"))
                return result
            else:
                logger.warning("Orchestrator returned HTTP %s: %s", resp.status_code, resp.text)
                return {"error": "ORCHESTRATOR_HTTP_ERROR", "status_code": resp.status_code}
        except Exception as e:
            logger.info("Orchestrator HTTP call failed (using direct fallback): %s", e)
            # Direct in-process fallback
            from orchestrator_agent.agent import OrchestratorService
            orch = OrchestratorService()
            return await orch.process_transaction_alert(order_data)


# --------------------------------------------------------------------------
# Endpoints: PayPal Webhooks & Attack Simulation
# --------------------------------------------------------------------------

@app.post("/webhooks/paypal")
async def paypal_webhook_listener(request: Request, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Official PayPal Webhook receiver.
    Receives live events from developer.paypal.com/dashboard/webhooksSimulator:
    - CHECKOUT.ORDER.APPROVED
    - PAYMENT.CAPTURE.COMPLETED
    - PAYMENT.CAPTURE.DENIED
    - CUSTOMER.DISPUTE.CREATED
    """
    global monitor_agent
    if monitor_agent is None:
        monitor_agent = TransactionMonitorAgent()

    try:
        body = await request.json()
        event_type = body.get("event_type", "UNKNOWN_EVENT")
        event_id = body.get("id", "UNKNOWN_ID")
        resource = body.get("resource", {})

        logger.info("Received PayPal Webhook [%s] ID: %s", event_type, event_id)

        # Process the order or capture in the resource
        order_data = resource if "purchase_units" in resource or "intent" in resource else {"id": resource.get("id"), "raw_resource": resource}

        # Dispatch to orchestrator
        background_tasks.add_task(monitor_agent.forward_to_orchestrator, order_data)

        return {
            "status": "ACCEPTED",
            "event_id": event_id,
            "event_type": event_type,
            "dispatched_to_aegispay_swarm": True,
        }
    except Exception as e:
        logger.error("Error processing PayPal webhook payload: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {str(e)}")


@app.post("/simulate-attack/{scenario}")
async def simulate_attack_endpoint(scenario: str) -> Dict[str, Any]:
    """
    Trigger an instant simulated fraud attack for live judge demos:
    - account_takeover
    - card_testing_bot
    - chargeback_exploit
    - legitimate_order
    """
    global monitor_agent
    if monitor_agent is None:
        monitor_agent = TransactionMonitorAgent()

    scenario_map = {
        "account_takeover": FraudScenario.ACCOUNT_TAKEOVER,
        "ato": FraudScenario.ACCOUNT_TAKEOVER,
        "card_testing_bot": FraudScenario.CARD_TESTING_BOT,
        "bot": FraudScenario.CARD_TESTING_BOT,
        "chargeback_exploit": FraudScenario.CHARGEBACK_EXPLOIT,
        "dispute": FraudScenario.CHARGEBACK_EXPLOIT,
        "legitimate_order": FraudScenario.LEGITIMATE_ORDER,
        "legit": FraudScenario.LEGITIMATE_ORDER,
    }
    selected_scenario = scenario_map.get(scenario.lower(), FraudScenario.ACCOUNT_TAKEOVER)

    order = monitor_agent.paypal_client.simulator.generate_simulated_order(selected_scenario)
    logger.info("Triggering simulated attack scenario: %s (Order %s)", selected_scenario.value, order.get("id"))
    result = await monitor_agent.forward_to_orchestrator(order)
    return result


@app.post("/stream/start")
async def start_stream_endpoint():
    global monitor_agent
    if monitor_agent is None:
        monitor_agent = TransactionMonitorAgent()
    await monitor_agent.start_stream()
    return {"status": "STREAMING_ACTIVE", "poll_interval_seconds": monitor_agent.poll_interval}


@app.post("/stream/stop")
async def stop_stream_endpoint():
    global monitor_agent
    if monitor_agent is None:
        monitor_agent = TransactionMonitorAgent()
    await monitor_agent.stop_stream()
    return {"status": "STREAMING_STOPPED"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "transaction_monitor_agent", "mode": "paypal_commerce"}


def main():
    logger.info("Starting TransactionMonitorAgent on port 8083...")
    global monitor_agent
    monitor_agent = TransactionMonitorAgent()
    uvicorn.run(app, host="0.0.0.0", port=8083, log_level="info")


if __name__ == "__main__":
    main()
