# Copyright 2026 AegisPay Authors
# PayPal Commerce Entity Models & Risk Schemas

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json


@dataclass
class Money:
    currency_code: str = "USD"
    value: str = "0.00"

    @property
    def float_value(self) -> float:
        try:
            return float(self.value)
        except (ValueError, TypeError):
            return 0.0


@dataclass
class Payer:
    payer_id: str
    email_address: str
    name: Dict[str, str] = field(default_factory=dict)
    phone: Optional[str] = None
    address: Dict[str, str] = field(default_factory=dict)
    account_age_days: Optional[int] = None
    dispute_count_last_90d: int = 0


@dataclass
class PurchaseItem:
    name: str
    quantity: str
    unit_amount: Money
    sku: Optional[str] = None
    category: str = "PHYSICAL_GOODS"


@dataclass
class ShippingDetail:
    recipient_name: str
    address_line_1: str
    admin_area_2: str  # City
    admin_area_1: str  # State
    postal_code: str
    country_code: str = "US"


@dataclass
class PurchaseUnit:
    reference_id: str
    amount: Money
    items: List[PurchaseItem] = field(default_factory=list)
    shipping: Optional[ShippingDetail] = None
    payments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PayPalOrder:
    id: str
    status: str  # CREATED, APPROVED, COMPLETED, VOIDED
    intent: str  # CAPTURE, AUTHORIZE
    create_time: str
    update_time: str
    payer: Optional[Payer] = None
    purchase_units: List[PurchaseUnit] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)

    @property
    def total_amount(self) -> float:
        if not self.purchase_units:
            return 0.0
        return sum(unit.amount.float_value for unit in self.purchase_units)

    @property
    def currency(self) -> str:
        if self.purchase_units:
            return self.purchase_units[0].amount.currency_code
        return "USD"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PayPalPaymentCapture:
    id: str
    status: str  # COMPLETED, DECLINED, PARTIALLY_REFUNDED, PENDING, REFUNDED
    amount: Money
    final_capture: bool = True
    seller_protection: Dict[str, str] = field(default_factory=lambda: {"status": "ELIGIBLE"})
    create_time: str = ""
    update_time: str = ""
    links: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PayPalAuthorization:
    id: str
    status: str  # CREATED, CAPTURED, DENIED, EXPIRED, VOIDED, PENDING
    amount: Money
    expiration_time: str = ""
    create_time: str = ""
    update_time: str = ""
    links: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PayPalRefund:
    id: str
    status: str  # COMPLETED, PENDING, CANCELLED, FAILED
    amount: Money
    note_to_payer: str = ""
    create_time: str = ""
    update_time: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PayPalDispute:
    dispute_id: str
    create_time: str
    status: str  # OPEN, UNDER_REVIEW, RESOLVED, CLOSED
    dispute_amount: Money
    dispute_reason: str  # UNAUTHORISED, MERCHANDISE_OR_SERVICE_NOT_RECEIVED
    dispute_life_cycle_stage: str = "CHARGEBACK"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PayPalWebhookEvent:
    id: str
    event_version: str
    create_time: str
    event_type: str  # CHECKOUT.ORDER.APPROVED, PAYMENT.CAPTURE.COMPLETED, etc.
    resource_type: str
    resource: Dict[str, Any]
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class FraudRiskAssessment:
    transaction_id: str
    order_id: str
    risk_score: float  # 0.0 to 10.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    action_recommended: str  # APPROVE, FLAG_FOR_REVIEW, VOID_AUTHORIZATION, REFUND_CAPTURE
    reasons: List[str] = field(default_factory=list)
    justification: str = ""
    tokens_used: int = 0
    decision_latency_ms: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
