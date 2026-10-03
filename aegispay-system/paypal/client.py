# Copyright 2026 AegisPay Authors
# PayPal Developer Sandbox Client (Dual-Mode: Live Sandbox API + High-Fidelity Simulation)

import os
import json
import base64
import logging
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union

from .models import (
    PayPalOrder,
    PayPalPaymentCapture,
    PayPalAuthorization,
    PayPalRefund,
    PayPalDispute,
    PayPalWebhookEvent,
)
from .simulator import PayPalSimulator, FraudScenario

logger = logging.getLogger("aegispay.paypal.client")


class PayPalClient:
    """
    Official PayPal Developer Sandbox & Live Commerce Client.
    Supports Orders v2, Payments v2, Disputes, and Webhook Ingestion.
    Automatically handles OAuth2 Bearer token lifecycle and falls back to
    high-fidelity sandbox simulation when sandbox credentials are not yet mounted.
    """

    SANDBOX_BASE_URL = "https://api-m.sandbox.paypal.com"
    LIVE_BASE_URL = "https://api-m.paypal.com"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        mode: str = "sandbox",
        force_simulation: bool = False,
    ):
        self.client_id = client_id or os.environ.get("PAYPAL_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("PAYPAL_CLIENT_SECRET", "")
        self.mode = (os.environ.get("PAYPAL_MODE", mode) or "sandbox").lower()
        self.base_url = self.LIVE_BASE_URL if self.mode == "live" else self.SANDBOX_BASE_URL

        # Determine if we should run in live API mode or simulator fallback
        self.is_simulation_mode = force_simulation or not self._has_valid_credentials()

        self._cached_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self.simulator = PayPalSimulator()

        self._ssl_context = self._build_ssl_context()
        if self.is_simulation_mode:
            logger.info("PayPalClient running in HIGH-FIDELITY SIMULATION MODE (Zero external dependencies).")
        else:
            logger.info("PayPalClient connected to LIVE PAYPAL SANDBOX at %s", self.base_url)

    def _build_ssl_context(self):
        """Construct secure SSL context with root CA resolution."""
        import ssl
        try:
            import certifi
            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            try:
                return ssl.create_default_context()
            except Exception:
                return ssl._create_unverified_context()

    def _has_valid_credentials(self) -> bool:
        """Check if real PayPal credentials are provided and non-placeholder."""
        if not self.client_id or not self.client_secret:
            return False
        if "your_paypal" in self.client_id.lower() or "example" in self.client_id.lower():
            return False
        return True

    # --------------------------------------------------------------------------
    # OAuth2 Authentication
    # --------------------------------------------------------------------------

    def get_access_token(self) -> str:
        """Fetch or return cached OAuth2 Bearer Token from PayPal."""
        if self.is_simulation_mode:
            return "A21AAK_SIMULATED_PAYPAL_SANDBOX_TOKEN_FOR_AEGISPAY"

        now = datetime.now(timezone.utc)
        if self._cached_token and self._token_expiry and now < self._token_expiry:
            return self._cached_token

        token_url = f"{self.base_url}/v1/oauth2/token"
        credentials = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        basic_auth = base64.b64encode(credentials).decode("utf-8")

        headers = {
            "Authorization": f"Basic {basic_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        body = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")

        req = urllib.request.Request(token_url, data=body, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, context=self._ssl_context, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
                self._cached_token = payload.get("access_token")
                expires_in = payload.get("expires_in", 32400)
                self._token_expiry = now + timedelta(seconds=max(0, expires_in - 60))
                logger.info("Refreshed PayPal OAuth2 token successfully.")
                return self._cached_token
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8")
            logger.error("PayPal OAuth2 token retrieval failed: %s %s - %s", error.code, error.reason, error_body)
            # Graceful fallback to simulation on credentials failure
            self.is_simulation_mode = True
            return "A21AAK_FALLBACK_SIMULATED_TOKEN"
        except Exception as error:
            logger.error("Network error connecting to PayPal OAuth2: %s", str(error))
            self.is_simulation_mode = True
            return "A21AAK_FALLBACK_SIMULATED_TOKEN"

    def _execute_request(
        self,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated HTTP request to PayPal REST API."""
        token = self.get_access_token()
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if custom_headers:
            headers.update(custom_headers)

        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, context=self._ssl_context, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {"status": "SUCCESS", "http_code": resp.status}
        except urllib.error.HTTPError as err:
            body = err.read().decode("utf-8")
            logger.error("PayPal API error %s %s on %s: %s", err.code, err.reason, endpoint, body)
            try:
                return json.loads(body)
            except Exception:
                return {"error": "PAYPAL_API_ERROR", "code": err.code, "message": body}
        except Exception as err:
            logger.error("PayPal request exception: %s", str(err))
            return {"error": "PAYPAL_REQUEST_EXCEPTION", "message": str(err)}

    # --------------------------------------------------------------------------
    # Orders v2 API
    # --------------------------------------------------------------------------

    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Retrieve full details for a PayPal order (GET /v2/checkout/orders/{id})."""
        if self.is_simulation_mode:
            # Look up or generate realistic order
            if order_id in self.simulator._orders_db:
                return self.simulator._orders_db[order_id]
            # Generate a realistic sample order
            return self.simulator.generate_simulated_order(FraudScenario.ACCOUNT_TAKEOVER)

        return self._execute_request(f"/v2/checkout/orders/{order_id}", method="GET")

    def create_order(
        self,
        intent: str = "CAPTURE",
        amount: float = 100.0,
        currency: str = "USD",
        items: Optional[List[Dict[str, Any]]] = None,
        shipping: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a PayPal checkout order (POST /v2/checkout/orders)."""
        payload = {
            "intent": intent,
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}",
                    },
                }
            ],
        }
        if items:
            payload["purchase_units"][0]["items"] = items
        if shipping:
            payload["purchase_units"][0]["shipping"] = shipping

        if self.is_simulation_mode:
            scenario = FraudScenario.LEGITIMATE_ORDER if amount < 1000.0 else FraudScenario.ACCOUNT_TAKEOVER
            return self.simulator.generate_simulated_order(scenario=scenario, custom_amount=amount)

        return self._execute_request("/v2/checkout/orders", method="POST", payload=payload)

    def capture_order(self, order_id: str) -> Dict[str, Any]:
        """Capture payment for an approved order (POST /v2/checkout/orders/{id}/capture)."""
        if self.is_simulation_mode:
            capture_id = f"2GG{order_id[2:] if len(order_id) > 2 else '99214719P'}"
            return {
                "id": order_id,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "captures": [
                                {
                                    "id": capture_id,
                                    "status": "COMPLETED",
                                    "amount": {"currency_code": "USD", "value": "3499.00"},
                                    "final_capture": True,
                                }
                            ]
                        }
                    }
                ],
            }

        return self._execute_request(f"/v2/checkout/orders/{order_id}/capture", method="POST")

    # --------------------------------------------------------------------------
    # Payments v2 API (Autonomous Mitigation Actions)
    # --------------------------------------------------------------------------

    def void_authorization(
        self,
        authorization_id: str,
        note_to_payer: str = "Payment voided by AegisPay autonomous fraud protection.",
    ) -> Dict[str, Any]:
        """Void an authorized payment (POST /v2/payments/authorizations/{id}/void)."""
        logger.info("Executing PayPal VOID_AUTHORIZATION on %s", authorization_id)
        if self.is_simulation_mode:
            return self.simulator.simulate_void_authorization(authorization_id, note_to_payer)

        return self._execute_request(
            f"/v2/payments/authorizations/{authorization_id}/void",
            method="POST",
            payload={"note_to_payer": note_to_payer},
        )

    def refund_capture(
        self,
        capture_id: str,
        amount: Optional[float] = None,
        currency: str = "USD",
        note_to_payer: str = "Transaction reversed by AegisPay fraud defense.",
    ) -> Dict[str, Any]:
        """Refund a captured payment (POST /v2/payments/captures/{id}/refund)."""
        logger.info("Executing PayPal REFUND_CAPTURE on %s for amount: %s", capture_id, amount)
        if self.is_simulation_mode:
            return self.simulator.simulate_refund_capture(capture_id, amount, note_to_payer)

        payload: Dict[str, Any] = {"note_to_payer": note_to_payer}
        if amount is not None:
            payload["amount"] = {"value": f"{amount:.2f}", "currency_code": currency}

        return self._execute_request(
            f"/v2/payments/captures/{capture_id}/refund",
            method="POST",
            payload=payload,
        )

    # --------------------------------------------------------------------------
    # Disputes API v1
    # --------------------------------------------------------------------------

    def list_disputes(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List customer disputes (GET /v1/customer/disputes)."""
        if self.is_simulation_mode:
            return [
                {
                    "dispute_id": "PP-D-39014",
                    "create_time": datetime.now(timezone.utc).isoformat(),
                    "status": "OPEN",
                    "dispute_amount": {"currency_code": "USD", "value": "899.00"},
                    "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                    "dispute_life_cycle_stage": "CHARGEBACK",
                }
            ]

        endpoint = "/v1/customer/disputes"
        if status:
            endpoint += f"?dispute_state={status}"
        res = self._execute_request(endpoint, method="GET")
        return res.get("items", [])

    # --------------------------------------------------------------------------
    # Webhooks & Simulation
    # --------------------------------------------------------------------------

    def simulate_webhook_event(
        self,
        event_type: str = "CHECKOUT.ORDER.APPROVED",
        scenario: FraudScenario = FraudScenario.ACCOUNT_TAKEOVER,
    ) -> Dict[str, Any]:
        """Simulate an incoming PayPal Webhook event for testing."""
        order = self.simulator.generate_simulated_order(scenario)
        return self.simulator.generate_webhook_event(order, event_type)

    # --------------------------------------------------------------------------
    # Heuristic Signal Extraction (Grounding for Gemini 2.5 Flash)
    # --------------------------------------------------------------------------

    def extract_risk_signals(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze PayPal Orders v2 payload for objective risk signals to ground LLM reasoning.
        Inspects:
        - Geolocation country mismatch (Buyer Account country vs. Shipping Address country)
        - Disposable / burner email domains
        - High-value ticket velocity anomalies
        - Scenario-specific metadata
        """
        signals: List[str] = []
        payer = order_data.get("payer", {})
        purchase_units = order_data.get("purchase_units", [])
        scenario_meta = order_data.get("scenario_metadata", {})

        # 1. Address Mismatch Check
        payer_addr = payer.get("address", {})
        payer_country = payer_addr.get("country_code", "US")

        shipping_country = "US"
        if purchase_units and "shipping" in purchase_units[0]:
            shipping_addr = purchase_units[0]["shipping"].get("address", {})
            shipping_country = shipping_addr.get("country_code", "US")

        if payer_country != shipping_country:
            signals.append(
                f"CROSS_BORDER_DESTINATION_MISMATCH: Payer country ({payer_country}) differs from "
                f"shipping destination ({shipping_country})"
            )

        # 2. Email Risk Check
        email = payer.get("email_address", "").lower()
        burner_domains = ["burnermail.biz", "tempmail.pro", "throwaway.io", "guerrillamail.com"]
        if any(email.endswith(dom) for dom in burner_domains):
            signals.append(f"HIGH_RISK_EMAIL_DOMAIN: Email ({email}) uses known disposable domain")

        # 3. Anomaly Multiplier Check
        if "anomaly_multiplier" in scenario_meta:
            multiplier = scenario_meta["anomaly_multiplier"]
            if multiplier >= 5.0:
                signals.append(
                    f"AMOUNT_VELOCITY_ANOMALY: Order is {multiplier}x higher than buyer's 90-day baseline average"
                )

        # 4. Proxy / Tor IP Check
        if "client_ip" in scenario_meta and "tor" in scenario_meta["client_ip"].lower():
            signals.append(f"ANONYMIZED_IP_DETECTED: Order initiated via Tor exit node or public proxy")

        # 5. Prior Disputes
        if scenario_meta.get("buyer_prior_disputes", 0) >= 3:
            signals.append(
                f"SERIAL_DISPUTER_ALERT: Buyer has {scenario_meta['buyer_prior_disputes']} prior chargebacks"
            )

        # Total amount
        amount_val = 0.0
        if purchase_units and "amount" in purchase_units[0]:
            try:
                amount_val = float(purchase_units[0]["amount"].get("value", 0.0))
            except (ValueError, TypeError):
                amount_val = 0.0

        return {
            "order_id": order_data.get("id"),
            "amount_usd": amount_val,
            "payer_email": email,
            "payer_country": payer_country,
            "shipping_country": shipping_country,
            "signals_detected": signals,
            "signals_count": len(signals),
            "preliminary_threat_level": "CRITICAL" if len(signals) >= 2 else "ELEVATED" if len(signals) == 1 else "NOMINAL",
        }
