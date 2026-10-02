# Copyright 2026 AegisPay Authors
# End-to-End Multi-Agent Swarm Verification Suite

import os
import sys
import asyncio
import json

# Ensure root and aegispay-system are in sys.path
BASE_DIR = os.path.dirname(__file__)
sys.path.insert(0, BASE_DIR)

from paypal import PayPalClient, FraudScenario
from orchestrator_agent.agent import OrchestratorService
from transaction_monitor_agent.agent import TransactionMonitorAgent


async def run_swarm_verification():
    print("=" * 80)
    print("      AEGISPAY AUTONOMOUS MULTI-AGENT SWARM VERIFICATION (PAYPAL COMMERCE)")
    print("=" * 80)

    monitor = TransactionMonitorAgent()
    orchestrator = OrchestratorService()

    scenarios = [
        (FraudScenario.ACCOUNT_TAKEOVER, "Account Takeover (ATO) - Tor Proxy & Destination Mismatch", True),
        (FraudScenario.CARD_TESTING_BOT, "Card Testing Bot - Micro-amount velocity & Burner Domain", True),
        (FraudScenario.CHARGEBACK_EXPLOIT, "Friendly Fraud - Serial Disputer exploiting capture", True),
        (FraudScenario.LEGITIMATE_ORDER, "Legitimate Verified Commerce - 4.5yr VIP buyer", False),
    ]

    for idx, (scenario, desc, expected_actuation) in enumerate(scenarios, 1):
        print(f"\n[{idx}/4] SCENARIO: {desc}")
        order = monitor.paypal_client.simulator.generate_simulated_order(scenario)
        order_id = order.get("id")
        amount = order.get("purchase_units", [{}])[0].get("amount", {}).get("value")
        print(f"      PayPal Order: {order_id} (Amount: ${amount})")

        result = await orchestrator.process_transaction_alert(order)

        risk_score = result.get("risk_score")
        risk_level = result.get("risk_level")
        should_actuate = result.get("should_actuate")
        summary = result.get("summary")
        signals = result.get("signals", [])

        print(f"      Risk Score  : {risk_score}/10.0 [{risk_level}]")
        print(f"      Signals ({len(signals)}): {signals[:2]}")
        print(f"      Actuated    : {should_actuate} (Expected: {expected_actuation})")
        print(f"      Audit Trail : {summary}")

        assert should_actuate == expected_actuation, f"Actuation mismatch for {scenario}: got {should_actuate}, expected {expected_actuation}"
        print(f"      -> Scenario {idx} PASSED")

    print("\n" + "=" * 80)
    print("  SUCCESS: ALL 4 MULTI-AGENT PAYPAL FRAUD SCENARIOS VERIFIED END-TO-END!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_swarm_verification())
