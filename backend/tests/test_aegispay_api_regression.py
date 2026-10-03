"""API regression tests for core AegisPay orchestrator and simulation flows."""

import os
import time
import uuid
import requests


BASE_URL = os.environ.get("preview_endpoint")


def _base_url() -> str:
    assert BASE_URL, "preview_endpoint environment variable is required"
    return BASE_URL.rstrip("/")


def _post_json(path: str, payload: dict, timeout: int = 45):
    return requests.post(f"{_base_url()}{path}", json=payload, timeout=timeout)


def test_health_endpoint():
    """Health endpoint: status and service metadata."""
    response = requests.get(f"{_base_url()}/health", timeout=20)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "orchestrator_agent"


def test_sse_stream_headers():
    """SSE endpoint: should expose event-stream response type."""
    response = requests.get(f"{_base_url()}/events/stream", stream=True, timeout=20)
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "text/event-stream" in content_type
    response.close()


def test_simulate_legitimate_order():
    """Simulation API: legitimate_order should return complete decision record."""
    response = requests.post(f"{_base_url()}/simulate-scenario/legitimate_order", timeout=60)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("order_id"), str) and data["order_id"]
    assert isinstance(data.get("risk_score"), (int, float))
    assert "should_actuate" in data
    assert isinstance(data.get("transaction_data"), dict)


def test_simulate_cart_tampering():
    """Simulation API: cart_tampering should include investigation payload."""
    response = requests.post(f"{_base_url()}/simulate-scenario/cart_tampering", timeout=60)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"]
    assert isinstance(data.get("investigation_result"), dict)
    assert "fraud_analysis" in data["investigation_result"]


def test_process_transaction_custom_payload():
    """Process transaction API: accepts custom payload and returns evaluated record."""
    unique_suffix = str(uuid.uuid4())[:8]
    payload = {
        "id": f"5OTESTTXN{unique_suffix.upper()}",
        "intent": "CAPTURE",
        "amount": 125.5,
        "payer": {
            "payer_id": f"TEST-PAYER-{unique_suffix.upper()}",
            "email_address": f"test-{unique_suffix}@example.com",
            "name": {"given_name": "Test", "surname": "Buyer"},
        },
        "purchase_units": [
            {
                "amount": {"value": "125.50", "currency_code": "USD"},
                "items": [
                    {
                        "name": "Electronics & Hardware",
                        "quantity": "1",
                        "unit_amount": {"value": "125.50", "currency_code": "USD"},
                    }
                ],
                "shipping": {"address": {"admin_area_2": "Austin", "country_code": "US"}},
            }
        ],
        "create_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    response = _post_json("/process-transaction", payload, timeout=70)
    assert response.status_code == 200
    data = response.json()
    assert data.get("order_id")
    assert isinstance(data.get("risk_score"), (int, float))
    assert isinstance(data.get("summary"), str) and data["summary"]
    assert isinstance(data.get("investigation_result"), dict)


def test_kernel_health_endpoint():
    """Kernel health API: should return structured health payload."""
    response = requests.get(f"{_base_url()}/api/kernel/health", timeout=45)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert any(key in data for key in ["status", "service", "mode", "provider"])


def test_zapier_health_endpoint():
    """Zapier health API: endpoint responds with integration metadata."""
    response = requests.get(f"{_base_url()}/api/zapier/health", timeout=45)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert any(key in data for key in ["status", "service", "available_tools", "provider"])
