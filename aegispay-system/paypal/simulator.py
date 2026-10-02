# Copyright 2026 AegisPay Authors
# High-Fidelity PayPal Sandbox Commerce & Fraud Attack Simulator

import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

from .models import (
    PayPalOrder,
    PurchaseUnit,
    PurchaseItem,
    Money,
    Payer,
    ShippingDetail,
    PayPalPaymentCapture,
    PayPalAuthorization,
    PayPalWebhookEvent,
    PayPalDispute,
)


class FraudScenario(str, Enum):
    LEGITIMATE_ORDER = "LEGITIMATE_ORDER"
    ACCOUNT_TAKEOVER = "ACCOUNT_TAKEOVER"
    CARD_TESTING_BOT = "CARD_TESTING_BOT"
    CHARGEBACK_EXPLOIT = "CHARGEBACK_EXPLOIT"
    HIGH_VELOCITY_BURST = "HIGH_VELOCITY_BURST"


class PayPalSimulator:
    """
    High-fidelity simulator of PayPal Developer Sandbox APIs and Webhook events.
    Enables autonomous agent end-to-end testing without external network bottlenecks,
    while producing byte-for-byte schema matches to PayPal Orders v2 and Payments v2.
    """

    def __init__(self):
        self._orders_db: Dict[str, Dict[str, Any]] = {}
        self._captures_db: Dict[str, Dict[str, Any]] = {}
        self._authorizations_db: Dict[str, Dict[str, Any]] = {}
        self._refunds_db: Dict[str, Dict[str, Any]] = {}
        self._disputes_db: Dict[str, Dict[str, Any]] = {}
        self._transaction_history: List[Dict[str, Any]] = []

    def generate_simulated_order(
        self,
        scenario: FraudScenario = FraudScenario.ACCOUNT_TAKEOVER,
        custom_amount: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate a complete PayPal Orders v2 payload for a specific scenario."""
        order_id = f"5O{random.randint(10000000, 99999999)}TN{random.randint(100000, 999999)}"
        now_iso = datetime.now(timezone.utc).isoformat()

        if scenario == FraudScenario.ACCOUNT_TAKEOVER:
            amount_val = custom_amount or 3499.00
            order = {
                "id": order_id,
                "status": "APPROVED",
                "intent": "CAPTURE",
                "create_time": now_iso,
                "update_time": now_iso,
                "scenario_metadata": {
                    "scenario": scenario.value,
                    "target_account": "victims_account@corporate.org",
                    "attack_vector": "Credential Stuffing + Cross-Border Freight Forwarder",
                    "client_ip": "185.220.101.44 (Tor Exit Node / Romania)",
                    "account_baseline_avg_usd": 145.0,
                    "anomaly_multiplier": round(amount_val / 145.0, 1),
                },
                "payer": {
                    "payer_id": f"PAYER-ATO-{uuid.uuid4().hex[:8].upper()}",
                    "email_address": "victims_account@corporate.org",
                    "name": {"given_name": "Eleanor", "surname": "Vance"},
                    "phone": {"phone_number": {"national_number": "2065550198"}},
                    "address": {
                        "country_code": "US",
                        "postal_code": "98101",
                        "admin_area_1": "WA",
                        "admin_area_2": "Seattle",
                    },
                },
                "purchase_units": [
                    {
                        "reference_id": f"PU-{uuid.uuid4().hex[:6].upper()}",
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{amount_val:.2f}",
                            "breakdown": {
                                "item_total": {"currency_code": "USD", "value": f"{amount_val:.2f}"}
                            },
                        },
                        "items": [
                            {
                                "name": "Apple MacBook Pro 16\" M3 Max - 64GB / 2TB SSD",
                                "quantity": "1",
                                "unit_amount": {"currency_code": "USD", "value": f"{amount_val:.2f}"},
                                "sku": "APL-MBP-16-M3X",
                                "category": "PHYSICAL_GOODS",
                            }
                        ],
                        "shipping": {
                            "name": {"full_name": "Rapid Reship Logistics Drop 4B"},
                            "address": {
                                "address_line_1": "Strada Academiei 14, Box 99",
                                "admin_area_2": "Bucharest",
                                "postal_code": "010014",
                                "country_code": "RO",
                            },
                        },
                    }
                ],
            }

        elif scenario == FraudScenario.CARD_TESTING_BOT:
            amount_val = custom_amount or round(random.uniform(1.20, 4.99), 2)
            order = {
                "id": order_id,
                "status": "APPROVED",
                "intent": "AUTHORIZE",
                "create_time": now_iso,
                "update_time": now_iso,
                "scenario_metadata": {
                    "scenario": scenario.value,
                    "attack_vector": "Automated Card Testing Script (18 requests/min)",
                    "client_ip": "45.142.122.9 (Known Proxy)",
                    "card_bin": "411111 (Visa / Unknown Issuer)",
                    "avs_result": "N (No Match)",
                },
                "payer": {
                    "payer_id": f"BOT-{uuid.uuid4().hex[:8].upper()}",
                    "email_address": f"test_{uuid.uuid4().hex[:6]}@burnermail.biz",
                    "name": {"given_name": "Test", "surname": "Buyer"},
                },
                "purchase_units": [
                    {
                        "reference_id": f"PU-TEST-{uuid.uuid4().hex[:6].upper()}",
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{amount_val:.2f}",
                        },
                        "items": [
                            {
                                "name": "Digital Gaming Credit Voucher $5",
                                "quantity": "1",
                                "unit_amount": {"currency_code": "USD", "value": f"{amount_val:.2f}"},
                                "category": "DIGITAL_GOODS",
                            }
                        ],
                    }
                ],
            }

        elif scenario == FraudScenario.CHARGEBACK_EXPLOIT:
            amount_val = custom_amount or 899.00
            order = {
                "id": order_id,
                "status": "APPROVED",
                "intent": "CAPTURE",
                "create_time": now_iso,
                "update_time": now_iso,
                "scenario_metadata": {
                    "scenario": scenario.value,
                    "buyer_prior_disputes": 5,
                    "dispute_rate_percentage": 71.4,
                    "attack_vector": "Friendly Fraud / False Item-Not-Received Claim",
                },
                "payer": {
                    "payer_id": f"PAYER-CB-{uuid.uuid4().hex[:8].upper()}",
                    "email_address": "serial_disputer_99@yahoo.com",
                    "name": {"given_name": "Marcus", "surname": "Corvin"},
                },
                "purchase_units": [
                    {
                        "reference_id": f"PU-{uuid.uuid4().hex[:6].upper()}",
                        "amount": {"currency_code": "USD", "value": f"{amount_val:.2f}"},
                        "items": [
                            {
                                "name": "Limited Edition Air Jordan Retro Sneakers",
                                "quantity": "1",
                                "unit_amount": {"currency_code": "USD", "value": f"{amount_val:.2f}"},
                            }
                        ],
                    }
                ],
            }

        else:  # LEGITIMATE_ORDER
            amount_val = custom_amount or 74.50
            order = {
                "id": order_id,
                "status": "APPROVED",
                "intent": "CAPTURE",
                "create_time": now_iso,
                "update_time": now_iso,
                "scenario_metadata": {
                    "scenario": scenario.value,
                    "buyer_account_tenure_years": 4.5,
                    "buyer_trust_tier": "VIP_VERIFIED",
                    "prior_disputes": 0,
                },
                "payer": {
                    "payer_id": "PAYER-LEGIT-VERIFIED-01",
                    "email_address": "sarah.jenkins@gmail.com",
                    "name": {"given_name": "Sarah", "surname": "Jenkins"},
                    "address": {
                        "country_code": "US",
                        "postal_code": "78701",
                        "admin_area_1": "TX",
                        "admin_area_2": "Austin",
                    },
                },
                "purchase_units": [
                    {
                        "reference_id": f"PU-{uuid.uuid4().hex[:6].upper()}",
                        "amount": {"currency_code": "USD", "value": f"{amount_val:.2f}"},
                        "items": [
                            {
                                "name": "Artisan Colombian Coffee Beans (2kg)",
                                "quantity": "1",
                                "unit_amount": {"currency_code": "USD", "value": f"{amount_val:.2f}"},
                            }
                        ],
                        "shipping": {
                            "name": {"full_name": "Sarah Jenkins"},
                            "address": {
                                "address_line_1": "401 Congress Ave, Suite 1200",
                                "admin_area_2": "Austin",
                                "admin_area_1": "TX",
                                "postal_code": "78701",
                                "country_code": "US",
                            },
                        },
                    }
                ],
            }

        self._orders_db[order_id] = order
        return order

    def generate_webhook_event(
        self,
        order: Dict[str, Any],
        event_type: str = "CHECKOUT.ORDER.APPROVED",
    ) -> Dict[str, Any]:
        """Wraps an order in standard PayPal Webhook event envelope."""
        event_id = f"WH-{uuid.uuid4().hex[:16].upper()}-{uuid.uuid4().hex[:16].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        return {
            "id": event_id,
            "event_version": "1.0",
            "create_time": now_iso,
            "resource_type": "checkout-order",
            "event_type": event_type,
            "summary": f"PayPal Order {order.get('id')} has been approved by the customer",
            "resource": order,
            "links": [
                {
                    "href": f"https://api-m.sandbox.paypal.com/v1/notifications/webhooks-events/{event_id}",
                    "rel": "self",
                    "method": "GET",
                }
            ],
        }

    def simulate_void_authorization(
        self,
        authorization_id: str,
        note: str = "Voided by AegisPay autonomous fraud shield",
    ) -> Dict[str, Any]:
        """Simulate PayPal Payments v2 Void Authorization."""
        now_iso = datetime.now(timezone.utc).isoformat()
        res = {
            "id": authorization_id,
            "status": "VOIDED",
            "note_to_payer": note,
            "update_time": now_iso,
            "links": [
                {
                    "href": f"https://api-m.sandbox.paypal.com/v2/payments/authorizations/{authorization_id}",
                    "rel": "self",
                    "method": "GET",
                }
            ],
        }
        self._authorizations_db[authorization_id] = res
        return res

    def simulate_refund_capture(
        self,
        capture_id: str,
        amount: Optional[float] = None,
        note: str = "Reversed by AegisPay autonomous fraud shield",
    ) -> Dict[str, Any]:
        """Simulate PayPal Payments v2 Refund Capture."""
        refund_id = f"REF-{uuid.uuid4().hex[:12].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        amount_str = f"{amount:.2f}" if amount else "3499.00"

        res = {
            "id": refund_id,
            "status": "COMPLETED",
            "amount": {"currency_code": "USD", "value": amount_str},
            "note_to_payer": note,
            "create_time": now_iso,
            "update_time": now_iso,
            "links": [
                {
                    "href": f"https://api-m.sandbox.paypal.com/v2/payments/refunds/{refund_id}",
                    "rel": "self",
                    "method": "GET",
                }
            ],
        }
        self._refunds_db[refund_id] = res
        return res
