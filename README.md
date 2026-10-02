# AegisPay — Autonomous Multi-Agent Fraud Shield for PayPal

[![PayPal](https://img.shields.io/badge/PayPal-Developer%20Platform-00457C?style=flat-square&logo=paypal&logoColor=white)](https://developer.paypal.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-8E75B2?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**AegisPay** is a proactive, hierarchical multi-agent AI system designed to safeguard PayPal merchants and agentic commerce workflows. It uses autonomous AI agents to detect, investigate, and mitigate high-risk transactions in real-time before costly chargebacks and fraud losses occur.

---

## Architecture Overview

AegisPay is structured as a decoupled multi-agent network where specialized AI agents collaborate using the **Agent-to-Agent (A2A)** protocol:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AEGISPAY FOR PAYPAL                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────────┐         A2A          ┌──────────────────────┐        │
│   │  Transaction     │ ───────────────────► │    Orchestrator      │        │
│   │  Monitor Agent   │                      │    Agent             │        │
│   │                  │                      │                      │        │
│   │  (Python/asyncio)│                      │  (ADK LlmAgent +     │        │
│   └────────┬─────────┘                      │   Gemini 2.5 Flash)  │        │
│            │                                └───────────┬──────────┘        │
│            │ REST / Webhook                       A2A   │   A2A             │
│            ▼                                 ┌──────────┴────────┐          │
│   ┌──────────────────┐                       ▼                   ▼          │
│   │  PayPal Ingestion│             ┌──────────────────┐ ┌─────────────────┐ │
│   │  / GenAI Toolbox │◄────────────│  Investigation   │ │  Actuator       │ │
│   │  Service         │◄────────────│  Agent           │ │  Agent          │ │
│   │                  │             │  (Gemini LLM)    │ │  (FastAPI)      │ │
│   └────────┬─────────┘             └──────────────────┘ └────────┬────────┘ │
│            │                                                     │          │
│            ▼                                                     ▼          │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                     PayPal Developer Platform                       │   │
│   │          (Orders API, Webhooks, Capture & Refund APIs)              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Specialized Multi-Agent System

| Component | Stack | Role |
| :--- | :--- | :--- |
| **Transaction Monitor Agent** | Python, asyncio, A2A SDK | Continuously monitors incoming payment events and flags high-risk transactions for investigation. |
| **Orchestrator Agent** | Google ADK, Gemini 2.5 Flash, A2A | The central command agent. Orchestrates case delegation, assesses risk thresholds, and issues enforcement commands. |
| **Investigation Agent** | Google ADK, Gemini 2.5 Flash, FastAPI | The intelligence investigator. Analyzes user history, transaction velocity, geographic consistency, and generates risk scores (0–10) with reasoning. |
| **Actuator Agent** | FastAPI, A2A SDK | The enforcement officer. Executes deterministic risk mitigation actions (e.g. holds, account locks, or refund authorizations). |
| **GenAI Toolbox Service** | REST API, Go / Python | Provides secure, isolated tool execution endpoints for database queries and external service interactions. |

---

## Detection & Mitigation Flow

1. **Monitor**: The Transaction Monitor ingests a new transaction event.
2. **Alert**: Sends a structured A2A message to the Orchestrator with transaction details.
3. **Investigate**: The Orchestrator delegates the alert to the Investigation Agent, which pulls customer context and past patterns.
4. **Assess**: The Investigation Agent uses Gemini 2.5 Flash to evaluate risk factors and produce a **Risk Score (0–10)** with clear textual justification.
5. **Decide**: The Orchestrator evaluates the risk score against the configured threshold (default: `7`).
6. **Act**: If the score meets or exceeds the threshold, the Orchestrator triggers the Actuator Agent to lock the account or initiate payment mitigation.

---

## Configuration

| Environment Variable | Target Component | Default | Description |
| :--- | :--- | :--- | :--- |
| `FRAUD_THRESHOLD` | Transaction Monitor | `1000.0` | Minimum transaction amount to flag for evaluation |
| `POLL_INTERVAL` | Transaction Monitor | `5` | Interval in seconds between ledger / event checks |
| `RISK_SCORE_THRESHOLD` | Orchestrator | `7` | Minimum risk score (out of 10) to trigger enforcement |
| `GEMINI_API_KEY` | Orchestrator, Investigation | — | Gemini API Key for LLM reasoning |
| `PAYPAL_CLIENT_ID` | System | — | PayPal Sandbox Client ID |
| `PAYPAL_CLIENT_SECRET`| System | — | PayPal Sandbox Client Secret |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
