# AegisPay — Devpost Hackathon Submission Form

**Hackathon**: *Build What's Next with PayPal and AI* (Devpost)  
**Repository**: [github.com/iykyk-vedant/Paypal-Hackathon_agiesPay](https://github.com/iykyk-vedant/Paypal-Hackathon_agiesPay)  
**License**: MIT License  

---

## 📌 Project Overview

* **Project Title**: AegisPay — Autonomous Multi-Agent AI Fraud Shield for PayPal Commerce
* **Short Tagline (1 sentence)**: A real-time, 4-agent autonomous AI defense swarm that intercepts Account Takeovers, Bot Bursts, and Fraudulent Disputes on PayPal Orders v2 & Payments v2 before chargebacks occur.

---

## 💡 Inspiration

In modern digital commerce, **the rise of agentic commerce** has created a profound trust gap. Autonomous AI agents are starting to make payments and buy products on behalf of humans. However, legacy fraud detection systems rely on archaic post-settlement reviews, rigid binary rules (e.g. "block any cart over $1,000"), and invasive human CAPTCHAs that disrupt checkout.

When account takeovers or bot card-testing attacks hit a merchant, the financial consequences are devastating:
1. **The Chargeback Cliff**: Merchants lose both merchandise and a non-refundable $15–$30 fee per disputed transaction.
2. **False Declines**: Up to 40% of blocked transactions are legitimate high-value purchases by loyal customers.
3. **Investigation Latency**: Human fraud desks take hours to investigate alerts, but digital goods and shipments escape in seconds.

We built **AegisPay** to turn fraud defense from a slow, reactive post-mortem into a **proactive, sub-second autonomous multi-agent shield** built directly on top of the PayPal Developer Platform.

---

## ⚙️ What It Does

AegisPay deploys a hierarchical 4-agent AI network communicating over the **Agent-to-Agent (A2A)** protocol:

1. **Transaction Monitor Agent (Port 8083)**: Ingests live PayPal webhooks (`CHECKOUT.ORDER.APPROVED`) and runs a background commerce sentinel.
2. **Orchestrator Agent (Port 8085)**: The central command leader. Delegates tasks, enforces decision doctrine, evaluates multi-factor risk scores against threshold (`7.0/10.0`), and broadcasts live Server-Sent Events (SSE).
3. **Investigation Agent (Port 8081)**: The AI detective. Combines **Google Gemini 2.5 Flash** with **APIMatic schema rules** to evaluate contextual indicators (Tor proxy IPs, 90-day velocity spikes, cross-border shipping mismatches, disposable burner domains).
4. **Actuator Agent (Port 8082)**: The policy enforcement officer. Executes deterministic financial actions on the **PayPal Payments v2 API**:
   - `POST /v2/payments/captures/{id}/refund`: Instantly reverses high-risk captured orders before delivery.
   - `POST /v2/payments/authorizations/{id}/void`: Instantly voids authorized payments to neutralize card-testing bots.

### Real-Time Surveillance Ops Center (AG Grid Enterprise)
All transactions and A2A telemetry stream in real-time into an ultra-responsive **AG Grid Quartz Dark** merchant portal:
- Live prepend row animations as orders occur.
- Color-coded risk badges (🟢 Safe 0-3.9, 🟡 Review 4-6.9, 🔴 Fraud 7-10).
- Interactive **Gemini AI Case File Drawer** with plain-English reasoning and PayPal refund receipts.
- Instant CSV surveillance audit exporter.

---

## 🏆 Sponsor Tracks & Capabilities Leveraged

### 1. PayPal Developer Platform (Core Requirement)
- Direct integration with `https://api-m.sandbox.paypal.com` with automatic OAuth2 Bearer token caching.
- Orders v2 API: Inspects order items, shipping destinations, and buyer identity.
- Payments v2 API: Autonomous `void_authorization` and `refund_capture`.
- Dual-mode architecture: Runs against live credentials or built-in high-fidelity sandbox simulation.

### 2. AG Grid Enterprise ($5,000 Sponsor Award)
- Customized Quartz Dark high-contrast styling with hardware-accelerated CSS and 0% idle GPU overhead.
- Live streaming table powered by `gridApi.applyTransaction({ add: [row], addIndex: 0 })`.
- Custom cell renderers for risk scores, status badges, and inline case file inspection.
- Instant client-side CSV compliance export.

### 3. Render ($5,000 Sponsor Award)
- Complete Infrastructure-as-Code Blueprint ([`render.yaml`](render.yaml)).
- Multi-service deployment: Python FastAPI Swarm API (`aegispay-swarm-api`) + Static AG Grid Dashboard (`aegispay-dashboard`).
- Integrated `/health` checks guaranteeing zero-downtime rolling deploys. Detailed in [`Docs/RENDER_DEPLOYMENT.md`](Docs/RENDER_DEPLOYMENT.md).

### 4. APIMatic ($1,000 Sponsor Award)
- Context Plugin ([`.apimatic/paypal_context_plugin.json`](.apimatic/paypal_context_plugin.json)) injects official PayPal OpenAPI schema constraints into the Investigation Agent's prompt context for zero-shot accuracy. Detailed in [`Docs/APIMATIC_USAGE.md`](Docs/APIMATIC_USAGE.md).

### 5. Astropods ($5,000 Sponsor Award)
- Validated containerized blueprint ([`astropods.yml`](astropods.yml)) and production agent card ([`AGENT.md`](AGENT.md)) authenticated and ready via `ast 0.27.0`.

### 6. Bryntum Scheduler ("Best Use of Bryntum" Sponsor Award)
- Embedded Bryntum Scheduler component (`dashboard/bryntum-scheduler.js`) providing an interactive Dispute Triage & Deadline Horizon view.
- Real-time resource timeline tracking allocations across Gemini AI agents and PayPal human dispute specialists.
- Dynamic dispute event plotting as transactions stream in from the live PayPal sentinel.

### 7. Channel3 ("Best Use of Channel3" - $2,500 Sponsor Award)
- Integrated Channel3 E-Commerce API (`aegispay-system/channel3/client.py`) across 100M+ products from 25,000+ retailers.
- Fair Market Value (FMV) verification detecting client-side DOM Cart Price Slashing (e.g. $3,499 MacBook Pro slashed to $149).
- Instant PayPal Payments v2 refund mitigation and dedicated Product Intelligence inspection drawer. Detailed in [`Docs/CHANNEL3_INTEGRATION.md`](Docs/CHANNEL3_INTEGRATION.md).

---

## 🛠️ How We Built It

- **Backend Swarm**: Python 3.10, FastAPI, Uvicorn, asyncio, HTTPX, Google ADK.
- **AI Reasoning**: Google Gemini 2.5 Flash (`google-genai` SDK).
- **Payment Engine**: Native Python PayPal REST Client (`aegispay-system/paypal/client.py`).
- **Product Intelligence**: Channel3 Product API (100M+ products, 25,000+ retailers).
- **Frontend & Surveillance**: AG Grid Enterprise v32+ (Quartz Dark), Bryntum Scheduler (Stockholm Dark), HTML5, Vanilla CSS, Server-Sent Events (SSE).
- **Tooling & Cloud**: Render Blueprints, Astropods CLI, APIMatic Context Plugin, Postman Collection v2.1.

---

## 🚧 Challenges We Ran Into

1. **A2A Swarm Synchronization**: Coordinating 4 distinct microservices without deadlock or latency spikes. We solved this with an async HTTPX connection pool and dual-mode in-process execution fallback.
2. **Sub-Second Investigation Latency**: Fraud mitigation must happen before order confirmation returns to the user. We optimized Gemini 2.5 Flash prompt payloads with APIMatic pre-computed heuristic vectors and Channel3 FMV checks, achieving sub-second P90 inference.
3. **High-Performance Dashboard Rendering**: Preventing browser freeze during rapid velocity attack bursts. We customized AG Grid's virtual DOM row renderer and eliminated costly box-shadow repaints.

---

## 🌟 Accomplishments That We're Proud Of

- **100% Native PayPal Payments v2 Execution**: Successfully executing real `refund_capture` and `void_authorization` calls in the PayPal Developer Sandbox.
- **Sub-Second Mitigation**: Reducing end-to-end fraud investigation and autonomous mitigation from hours of manual review to under 2 seconds.
- **Full 7-Sponsor Integration**: Seamlessly uniting PayPal, AG Grid, Render, APIMatic, Astropods, Bryntum, and Channel3 into a cohesive enterprise-grade application.

---

## 🔮 What's Next for AegisPay

- **Multi-Merchant Threat Intelligence**: Federated privacy-preserving threat intelligence sharing between participating PayPal merchants.
- **Biometric Behavioral Agent Fingerprinting**: Advanced telemetry for identifying bot purchase patterns in autonomous agentic commerce.
- **PayPal Dispute Auto-Arbitration**: Expanding the Actuator Agent to automatically compile and submit Gemini evidence packages directly into the PayPal Disputes API (`/v1/customer/disputes`).
