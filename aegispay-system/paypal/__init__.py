# AegisPay PayPal SDK & Client Package
"""
AegisPay PayPal integration package for PayPal Developer Sandbox.
Provides Orders v2, Payments v2 (void/refund), Disputes, and Webhooks handling.
"""

from .client import PayPalClient
from .models import (
    PayPalOrder,
    PayPalPaymentCapture,
    PayPalAuthorization,
    PayPalDispute,
    PayPalWebhookEvent,
    FraudRiskAssessment,
)
from .simulator import PayPalSimulator, FraudScenario

__all__ = [
    "PayPalClient",
    "PayPalSimulator",
    "FraudScenario",
    "PayPalOrder",
    "PayPalPaymentCapture",
    "PayPalAuthorization",
    "PayPalDispute",
    "PayPalWebhookEvent",
    "FraudRiskAssessment",
]
