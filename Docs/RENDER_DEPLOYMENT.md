# Deploying AegisPay on Render (Blueprint Specification)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/iykyk-vedant/Paypal-Hackathon_agiesPay)

This guide documents the Infrastructure-as-Code (IaC) Render Blueprint deployment for **AegisPay: Autonomous Multi-Agent AI Fraud Shield for PayPal Commerce**, submitted for the **"Best Deployment on Render"** Sponsor Award ($5,000).

---

## 1. Architecture on Render

AegisPay deploys on Render as a coordinated two-tier cloud architecture defined entirely in [`render.yaml`](../render.yaml):

```
                        ┌──────────────────────────────────────────────┐
                        │              Internet / Buyers               │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │          PayPal Developer Sandbox            │
                        │           api-m.sandbox.paypal.com           │
                        └──────────────────────┬───────────────────────┘
                                               │
                               Webhooks / REST │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Render Cloud Platform (Oregon Region)                                                       │
│                                                                                             │
│  ┌──────────────────────────────────────────┐     ┌──────────────────────────────────────┐  │
│  │ aegispay-swarm-api (Web Service)         │     │ aegispay-dashboard (Static Site)     │  │
│  │ • Python 3.10 Runtime                    │     │ • AG Grid Enterprise Quartz Dark     │  │
│  │ • FastAPI + Uvicorn Async Server         │     │ • Real-Time SSE Stream Listener      │  │
│  │ • Orchestrator + Swarm Agents            │     │ • Interactive Case File Drawer       │  │
│  │ • Health Check: /health                  │     │ • Instant CSV Audit Exporter         │  │
│  │ • Real-time SSE Stream: /events/stream   │     │                                      │  │
│  └────────────────────┬─────────────────────┘     └──────────────────▲───────────────────┘  │
│                       │                                              │                      │
│                       └──────────── Server-Sent Events (SSE) ────────┘                      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Service Breakdown

| Service Name | Render Type | Runtime | Port / Target | Purpose |
|---|---|---|---|---|
| `aegispay-swarm-api` | `web` | `python` (3.10) | `$PORT` (Dynamic) | Central FastAPI swarm orchestrator, PayPal Orders v2 & Payments v2 client, Gemini 2.5 Flash investigation, and SSE event streaming server. |
| `aegispay-dashboard` | `static` | `static` | `./dashboard` | Production AG Grid Enterprise Quartz Dark surveillance portal with real-time row animations, case file inspector drawer, and manual override triggers. |

---

## 2. Infrastructure as Code: `render.yaml`

The [`render.yaml`](../render.yaml) file defines the blueprint:

```yaml
version: "1"

services:
  - type: web
    name: aegispay-swarm-api
    runtime: python
    region: oregon
    plan: free
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: python aegispay-system/orchestrator_agent/agent.py
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.12
      - key: PAYPAL_MODE
        value: sandbox
      - key: RISK_SCORE_THRESHOLD
        value: "7.0"
      - key: PAYPAL_CLIENT_ID
        sync: false
      - key: PAYPAL_CLIENT_SECRET
        sync: false
      - key: GEMINI_API_KEY
        sync: false

  - type: static
    name: aegispay-dashboard
    runtime: static
    region: oregon
    plan: free
    staticPublishPath: ./dashboard
    autoDeploy: true
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

---

## 3. Environment Variable Security

Render securely manages environment variables marked with `sync: false`:

- `PAYPAL_CLIENT_ID`: Your PayPal Developer Sandbox REST App Client ID.
- `PAYPAL_CLIENT_SECRET`: Your PayPal Developer Sandbox REST App Secret.
- `GEMINI_API_KEY`: Google Gemini API Key for autonomous LLM fraud reasoning.
- `RISK_SCORE_THRESHOLD`: Policy threshold for automated intervention (default: `7.0`).
- `PAYPAL_MODE`: Set to `sandbox` for testing or `live` for production.

---

## 4. Health Checks & Zero-Downtime Deploys

The API service defines `healthCheckPath: /health`:
- Render automatically probes `GET /health` during deployment.
- Deploys are only routed once the API returns HTTP 200:
  ```json
  {
    "status": "healthy",
    "service": "orchestrator_agent",
    "mode": "paypal_commerce"
  }
  ```
- If an update fails health checks, Render keeps the previous build online, guaranteeing zero-downtime fraud surveillance for merchants.

---

## 5. One-Click Deployment Instructions

1. Click the **Deploy to Render** button above.
2. Sign in to your Render account (GitHub SSO supported).
3. Fill in your environment variables:
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_CLIENT_SECRET`
   - `GEMINI_API_KEY`
4. Click **Apply**.
5. Render automatically builds the Python FastAPI microservices, provisions the static AG Grid frontend, and wires the internal networking.
