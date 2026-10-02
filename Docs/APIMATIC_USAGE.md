# APIMatic Context Plugin Integration — AegisPay

## Overview

In **AegisPay**, autonomous AI agents (powered by Google Gemini 2.5 Flash and Google ADK) continuously inspect incoming PayPal transactions and take automated enforcement actions such as issuing refunds or voiding unauthorized payment captures.

To eliminate LLM hallucination and ensure strict schema compliance with PayPal's REST APIs, AegisPay integrates the **APIMatic Context Plugin for PayPal**.

---

## 1. Why APIMatic in AegisPay?

Large Language Models frequently hallucinate non-existent API parameters, mix up API versions (e.g. PayPal v1 vs v2 endpoints), or fail to supply required headers (such as `PayPal-Request-Id` for idempotency).

**APIMatic solves this by providing grounded, version-aware context directly to the AI agents:**

* **Schema Grounding**: Injects accurate parameter specifications for PayPal's Orders v2 and Payments v2 endpoints into agent tool definitions.
* **Idempotent Refund Enforcement**: Ensures that the `ActuatorAgent` uses the exact signature for `/v2/payments/captures/{capture_id}/refund` with unique UUID idempotency keys to prevent double-refunds.
* **Webhook Event Validation**: Provides the schema contract for ingesting `CHECKOUT.ORDER.APPROVED` and `PAYMENT.CAPTURE.COMPLETED` events in the `TransactionMonitorAgent`.

---

## 2. Repository Configuration

The APIMatic Context Plugin configuration is maintained at:
- [`.apimatic/paypal_context_plugin.json`](../.apimatic/paypal_context_plugin.json)

### Key Capabilities Contextualized:
1. **Orders API v2**: `get_order_details`, `authorize_order`, `capture_order`
2. **Payments API v2**: `refund_captured_payment`, `void_authorized_payment`
3. **Disputes API v1**: `list_disputes`, `get_dispute_details`
4. **Webhooks API v1**: Standard event payloads for automated monitoring

---

## 3. How the Agents Use the Context Plugin

```
┌─────────────────────────────────────────────────────────────┐
│                    AegisPay Multi-Agent Flow                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   [ PayPal Webhook ]                                        │
│          │                                                  │
│          ▼                                                  │
│   [ Transaction Monitor Agent ]                             │
│          │                                                  │
│          ▼ A2A                                              │
│   [ Orchestrator Agent ]                                    │
│          │                                                  │
│          ▼ A2A                                              │
│   [ Investigation Agent ] ◄── (APIMatic Context Plugin:     │
│          │                     Provides Orders & History    │
│          │                     API Schema to Gemini)        │
│          ▼                                                  │
│   [ Actuator Agent ]      ◄── (APIMatic Context Plugin:     │
│          │                     Provides type-safe PayPal    │
│          ▼                     Refund & Void API calls)     │
│   [ PayPal Sandbox API ]                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

1. **Investigation Agent Grounding**:
   The Investigation Agent calls PayPal's Orders API `/v2/checkout/orders/{id}` using the schema parameters validated by APIMatic to compare shipping vs billing metadata and account age.

2. **Actuator Agent Remediation**:
   When the fraud risk score reaches or exceeds the safety threshold ($\ge 7/10$), the Actuator executes:
   ```http
   POST /v2/payments/captures/{capture_id}/refund
   Content-Type: application/json
   PayPal-Request-Id: {uuid}
   Prefer: return=representation

   {
     "note_to_payer": "AegisPay autonomous security mitigation: suspicious transaction neutralized."
   }
   ```
   The APIMatic context ensures that the `note_to_payer` and header parameters adhere to PayPal's exact production specifications.

---

## 4. Summary for Reviewers

* **Tool**: APIMatic Context Plugin for PayPal.
* **Usage**: Injected into AegisPay's multi-agent autonomous framework to guarantee zero-hallucination PayPal API interactions.
* **Impact**: Enables safe, autonomous execution of critical financial actions (refunds and voids) in agentic commerce workflows.
