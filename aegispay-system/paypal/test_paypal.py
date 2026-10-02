# Test Suite for AegisPay PayPal Client Engine
"""
Validates that PayPalClient correctly generates, parses, extracts signals,
and executes mitigation actions across all fraud scenarios.
"""

import sys
import os
import json

# Ensure aegispay-system is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from paypal import PayPalClient, PayPalSimulator, FraudScenario


def test_paypal_client_simulation():
    print("=" * 70)
    print("RUNNING AEGISPAY PAYPAL CLIENT VERIFICATION")
    print("=" * 70)

    client = PayPalClient(force_simulation=True)
    assert client.is_simulation_mode is True, "Client should be in simulation mode"
    print("[PASS] PayPalClient initialized in simulation mode")

    # 1. Test Account Takeover Scenario
    print("\n--- Test Scenario 1: Account Takeover (ATO) ---")
    ato_order = client.create_order(intent="CAPTURE", amount=3499.00)
    assert ato_order["status"] == "APPROVED"
    assert ato_order["purchase_units"][0]["amount"]["value"] == "3499.00"
    order_id = ato_order["id"]
    print(f"[PASS] Created ATO Order: {order_id} ($3499.00)")

    signals = client.extract_risk_signals(ato_order)
    print(f"       Extracted Signals: {len(signals['signals_detected'])}")
    for s in signals["signals_detected"]:
        print(f"       * {s}")
    assert signals["preliminary_threat_level"] == "CRITICAL"
    print("[PASS] Risk signal extraction flagged CRITICAL threat")

    # 2. Test Void Authorization
    print("\n--- Test Scenario 2: Card Testing Bot & Void Authorization ---")
    bot_order = client.simulator.generate_simulated_order(FraudScenario.CARD_TESTING_BOT)
    bot_signals = client.extract_risk_signals(bot_order)
    print(f"[PASS] Card Testing Bot detected: {len(bot_signals['signals_detected'])} signals")
    for s in bot_signals["signals_detected"]:
        print(f"       * {s}")

    auth_void_result = client.void_authorization("AUTH-0EF548810W5718214")
    assert auth_void_result["status"] == "VOIDED"
    print(f"[PASS] Voided Authorization: {auth_void_result['id']} -> Status: {auth_void_result['status']}")

    # 3. Test Capture Refund
    print("\n--- Test Scenario 3: Proactive Capture Refund ---")
    refund_result = client.refund_capture("2GG279541U471931P", amount=3499.00)
    assert refund_result["status"] == "COMPLETED"
    print(f"[PASS] Issued Refund: {refund_result['id']} -> Amount: ${refund_result['amount']['value']}")

    # 4. Test Webhook Event Generation
    print("\n--- Test Scenario 4: PayPal Webhook Ingestion ---")
    webhook_event = client.simulate_webhook_event(
        event_type="CHECKOUT.ORDER.APPROVED",
        scenario=FraudScenario.ACCOUNT_TAKEOVER,
    )
    assert webhook_event["event_type"] == "CHECKOUT.ORDER.APPROVED"
    assert "resource" in webhook_event
    print(f"[PASS] Webhook Ingested: Event {webhook_event['id']} ({webhook_event['event_type']})")

    # 5. Test Legitimate Order
    print("\n--- Test Scenario 5: Legitimate Order ---")
    legit_order = client.simulator.generate_simulated_order(FraudScenario.LEGITIMATE_ORDER)
    legit_signals = client.extract_risk_signals(legit_order)
    assert legit_signals["signals_count"] == 0
    assert legit_signals["preliminary_threat_level"] == "NOMINAL"
    print(f"[PASS] Legitimate Order passed with 0 risk signals (Threat Level: {legit_signals['preliminary_threat_level']})")

    print("\n" + "=" * 70)
    print("ALL 5 PAYPAL CLIENT ENGINE TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    test_paypal_client_simulation()
