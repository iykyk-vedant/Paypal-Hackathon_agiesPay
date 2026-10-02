# AegisPay — Autonomous Multi-Agent Fraud Shield for PayPal Commerce

[![PayPal Sandbox](https://img.shields.io/badge/PayPal-Orders%20%26%20Payments%20v2-00457C?style=flat-square&logo=paypal&logoColor=white)](https://developer.paypal.com)
[![AG Grid Enterprise](https://img.shields.io/badge/AG%20Grid-Enterprise%20Quartz%20Dark-FD1D7C?style=flat-square&logo=ag-grid&logoColor=white)](https://www.ag-grid.com/)
[![Bryntum](https://img.shields.io/badge/Bryntum-Scheduler%20Dispute%20Horizon-4F46E5?style=flat-square)](https://bryntum.com/)
[![Channel3](https://img.shields.io/badge/Channel3-Product%20Data%20%26%20FMV-10B981?style=flat-square)](Docs/CHANNEL3_INTEGRATION.md)
[![Elastic](https://img.shields.io/badge/Elastic-Search%20%26%20ES|QL-005571?style=flat-square&logo=elastic&logoColor=white)](Docs/ELASTIC_INTEGRATION.md)
[![Render](https://img.shields.io/badge/Render-Blueprint%20IaC-46E3B7?style=flat-square&logo=render&logoColor=black)](https://render.com)
[![APIMatic](https://img.shields.io/badge/APIMatic-Context%20Plugin-0B78E3?style=flat-square)](Docs/APIMATIC_USAGE.md)
[![Astropods](https://img.shields.io/badge/Astropods-Agent%20Blueprint-9B51E0?style=flat-square)](AGENT.md)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-8E75B2?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev/)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/iykyk-vedant/Paypal-Hackathon_agiesPay)

**AegisPay** is a real-time, autonomous multi-agent AI fraud defense shield built for **PayPal Commerce**. Integrating directly with the official PayPal Developer Sandbox (Orders v2 & Payments v2 APIs), AegisPay pairs Google's Gemini 2.5 Flash reasoning model with APIMatic API context rules to detect, investigate, and autonomously mitigate payment fraud (e.g. Account Takeover, Card Testing Bots, Friendly Fraud) in sub-second latency before chargebacks occur.

All surveillance telemetry is broadcast live via Server-Sent Events (SSE) into a high-performance **AG Grid Enterprise** Ops Dashboard.

---

## Architecture Overview

```
                                  ┌──────────────────────────────────────────────┐
                                  │            PayPal Commerce Checkout          │
                                  │           api-m.sandbox.paypal.com           │
                                  └──────────────────────┬───────────────────────┘
                                                         │
                                    Orders v2 & Webhooks │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ AegisPay Hierarchical Multi-Agent Swarm (A2A Network)                                                  │
│                                                                                                        │
│   ┌─────────────────────────────┐         A2A Task         ┌───────────────────────────────────────┐   │
│   │ Transaction Monitor Agent   │ ───────────────────────► │ Orchestrator Agent                    │   │
│   │ (Sentinel / Webhook Engine) │                          │ (Central Command & Policy Engine)     │   │
│   │ Port: 8083                  │                          │ Port: 8085                            │   │
│   └─────────────────────────────┘                          └───────────────────┬───────────────────┘   │
│                                                                                │                       │
│                                                       ┌────────────────────────┴───────────────┐       │
│                                                       │ A2A Investigation                      │ A2A   │
│                                                       ▼                                        ▼ Act   │
│                                        ┌──────────────────────────────┐        ┌─────────────────────┐ │
│                                        │ Investigation Agent          │        │ Actuator Agent      │ │
│                                        │ • Gemini 2.5 Flash Reasoning │        │ • void_authorization│ │
│                                        │ • APIMatic Context Engine    │        │ • refund_capture    │ │
│                                        │ Port: 8081                   │        │ Port: 8082          │ │
│                                        └──────────────────────────────┘        └──────────┬──────────┘ │
│                                                                                           │            │
│                                                                                           ▼            │
│                                                                                ┌─────────────────────┐ │
│                                                                                │ PayPal Payments v2  │ │
│                                                                                └─────────────────────┘ │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                     Live SSE Event │ Stream (text/event-stream)
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ AG Grid Enterprise Real-Time Ops Dashboard (Port 8088)                                                 │
│ • Quartz Dark High-Contrast Theme with Hardware-Accelerated CSS                                        │
│ • Real-Time Row Transitions (Prepend Animated Ingestion)                                               │
│ • Interactive Gemini AI Case File Modal Drawer                                                         │
│ • Live Quick Scenarios: Account Takeover, Card Testing Bot, Friendly Fraud, Normal Order              │
│ • Instant CSV Surveillance Audit Exporter                                                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Sponsor Track Integrations

### 1. PayPal Developer Platform (Core Requirement)
- **Direct REST Integration**: Custom, robust Python client (`aegispay-system/paypal/client.py`) connecting to `https://api-m.sandbox.paypal.com` with automated OAuth2 Bearer token lifecycle.
- **Orders v2 API**: Inspects order items, shipping destinations, and buyer identity.
- **Payments v2 API**: Executes autonomous mitigations:
  - `POST /v2/payments/authorizations/{id}/void`: Void authorizations on high-risk card-testing bot transactions.
  - `POST /v2/payments/captures/{id}/refund`: Proactively reverse captured payments on compromised accounts before friendly fraud or chargeback fees hit.
- **Dual Mode**: Seamlessly operates against live PayPal Developer Sandbox credentials or high-fidelity simulation.

### 2. AG Grid Enterprise ($5,000 Sponsor Award)
- **Quartz Dark Custom Styling**: Fully custom-themed AG Grid Enterprise table with zero GPU lag and high accessibility.
- **Real-Time Row Ingestion**: Ingests new transactions dynamically at index 0 using `gridApi.applyTransaction({ add: [row], addIndex: 0 })`.
- **Dynamic Risk Score Cell Renderer**: Color-coded badges and risk indicator bars (Safe: 0-3.9, Review: 4.0-6.9, Fraud: 7.0-10.0).
- **Interactive Drawer**: Clicking any row pops the deep **Gemini AI Case File Inspector** showing decision justification and PayPal refund receipts.
- **Client-Side Export**: Integrated CSV exporter for instant compliance audit trails.

### 3. APIMatic ($1,000 Sponsor Award)
- **PayPal Context Plugin**: Context plugin located at [`.apimatic/paypal_context_plugin.json`](.apimatic/paypal_context_plugin.json).
- **Documentation**: Detailed guide at [`Docs/APIMATIC_USAGE.md`](Docs/APIMATIC_USAGE.md) demonstrating how APIMatic's schema metadata enhances the Investigation Agent's zero-shot fraud reasoning and field validation.

### 4. Astropods ($5,000 Sponsor Award)
- **Blueprint v1**: Fully validated [`astropods.yml`](astropods.yml) blueprint with resource allocations, environment secrets, and health checks.
- **Agent Card**: Production [`AGENT.md`](AGENT.md) specification card.
- **CLI Ready**: Compatible with `ast 0.27.0` for containerized agent packaging and deployment.

### 5. Render ($5,000 Sponsor Award)
- **Infrastructure as Code**: Production-grade [`render.yaml`](render.yaml) Blueprint.
- **Multi-Service Architecture**: Deploys the Python FastAPI swarm backend (`aegispay-swarm-api`) and the static AG Grid frontend (`aegispay-dashboard`).
- **Health Checks & Rolling Deploys**: Integrated `/health` checks ensure zero downtime during policy and model updates. See [`Docs/RENDER_DEPLOYMENT.md`](Docs/RENDER_DEPLOYMENT.md).

### 6. Bryntum Scheduler ("Best Use of Bryntum" Sponsor Award)
- **Interactive Dispute & Deadline Horizon**: High-performance Bryntum Scheduler component (`dashboard/bryntum-scheduler.js`) built with the Stockholm Dark theme.
- **Swarm Resource Timeline**: Tracks live resolution allocations across Gemini AI agents and PayPal dispute specialists.
- **Real-Time Streaming**: Automatically plots dispute windows and deadline alerts as transactions stream in from PayPal.

### 7. Channel3 ("Best Use of Channel3" - $2,500 Sponsor Award)
- **Fair Market Value (FMV) Verification**: Integrates Channel3 E-Commerce API (`aegispay-system/channel3/client.py`) across 100M+ products from 25,000+ retailers.
- **Cart Price Tampering Shield**: Detects client-side DOM price tampering (e.g. slashing a $3,499 MacBook Pro to $149) with sub-second precision.
- **Case File Product Card**: Visualizes verified brand, normalized retailer price, and variance pills inside the dashboard case file drawer. See [`Docs/CHANNEL3_INTEGRATION.md`](Docs/CHANNEL3_INTEGRATION.md).

### 8. Elastic Cloud ("Best Use of Elastic" Sponsor Award)
- **Serverless Vector Search & Threat Intel RAG**: Direct integration with Elastic Cloud 9.6.0 Serverless (`aegispay-system/elasticsearch/client.py`) searching historical fraud attack vectors with dense cosine similarity.
- **ES|QL Real-Time Velocity Analytics**: Employs Elasticsearch Query Language (ES|QL) piped query workflows to detect high-frequency bot bursts and anomalous spending clusters.
- **Dashboard Inspection Card**: Renders matched incident IDs (e.g. `#ATK-8812`), vector match percentages (`99.4%`), and live ES|QL signatures in the Case File Drawer. See [`Docs/ELASTIC_INTEGRATION.md`](Docs/ELASTIC_INTEGRATION.md).

---

## Multi-Agent Swarm Breakdown

| Agent | Port | Technology | Core Responsibility |
|---|---|---|---|
| **Transaction Monitor Agent** | `8083` | Python, FastAPI, asyncio | Ingests live PayPal webhooks (`CHECKOUT.ORDER.APPROVED`) and runs a background sentinel. |
| **Orchestrator Agent** | `8085` | FastAPI, SSE, A2A | Swarm commander. Evaluates findings against policy threshold (`7.0`), triggers actuation, and broadcasts SSE traces. |
| **Investigation Agent** | `8081` | Gemini 2.5 Flash, APIMatic | Extracts heuristic anomaly vectors (Tor proxy, velocity burst, cross-border mismatch) and reasons risk score. |
| **Actuator Agent** | `8082` | PayPal Payments v2 API | Executes deterministic financial mitigations (`refund_capture`, `void_authorization`). |

---

## Getting Started Locally

### Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox)

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/iykyk-vedant/Paypal-Hackathon_agiesPay.git
cd Paypal-Hackathon_agiesPay

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
Copy `.env.example` to `.env` and insert your credentials:
```bash
cp .env.example .env
```
Fill in:
```env
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_secret
PAYPAL_MODE=sandbox
GEMINI_API_KEY=your_gemini_api_key
RISK_SCORE_THRESHOLD=7.0
```

### 3. Start the Backend Swarm
```bash
# Start the central Orchestrator & SSE Stream service
python aegispay-system/orchestrator_agent/agent.py
```
*(Optionally start investigation, actuator, and monitor agents on ports 8081, 8082, 8083. If run standalone, the Orchestrator automatically invokes them in-process).*

### 4. Open the AG Grid Ops Dashboard
```bash
# Start the dashboard HTTP server
python -m http.server 8088 --directory dashboard
```
Open **`http://localhost:8088`** in your browser.

---

## Live Interactive Scenarios

On the Ops Dashboard, test any of the 4 live fraud scenarios:
- **`[Normal Order ($45.00)]`**: Low risk (1.2/10). Automatically cleared and approved.
- **`[High-Value Order ($1,499.00)]`**: Medium review (5.4/10). Flagged for review without blocking checkout.
- **`[Account Takeover ($4,850.00)]`**: Critical risk (9.4/10). Triggered by offshore Tor VPN and velocity spike. Swarm executes `refund_capture` via PayPal Payments v2 API.
- **`[Bot Burst ($1.28)]`**: High risk (7.8/10). Triggered by rapid-fire microtransactions with disposable emails. Swarm executes `void_authorization` via PayPal Payments v2 API.

Click any table row to inspect the full **Gemini AI Case File**, factor breakdown, and PayPal API receipts.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
