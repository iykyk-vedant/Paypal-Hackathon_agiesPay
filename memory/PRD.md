# AegisPay — Autonomous Multi-Agent Fraud Shield for PayPal Commerce

## Overview
Imported existing GitHub project (iykyk-vedant/Paypal-Hackathon_agiesPay). Python FastAPI
multi-agent swarm + AG Grid Enterprise ops dashboard. Built for PayPal hackathon.

## Architecture
- `aegispay-system/orchestrator_agent/agent.py` — Orchestrator (SSE, /simulate-scenario, /process-transaction). Default port 8085.
- Investigation / Actuator / Transaction Monitor agents (in-process fallback when standalone).
- Clients: PayPal (Orders v2 / Payments v2), Channel3 (FMV), Elastic (vector + ES|QL), Kernel (DOM audit).
- `dashboard/` — AG Grid Enterprise + Bryntum scheduler static dashboard.
- Investigation agent falls back to APIMatic-grounded heuristic engine when no GEMINI_API_KEY.

## Run setup (this environment)
- `/app/.env` — PayPal (live sandbox), Channel3, Elastic creds configured. No GEMINI key => heuristic mode. No KERNEL key => Kernel simulation mode.
- Deps: `pip install -r requirements.txt certifi`.
- Orchestrator (literal request): `python aegispay-system/orchestrator_agent/agent.py` on :8085 (nohup bg).
- Dashboard (literal request): `python -m http.server 8088 --directory dashboard` (nohup bg).
- Viewable Emergent preview: `preview_server.py` (orchestrator + StaticFiles) on :3000 via supervisor program `aegispay` (/etc/supervisor/conf.d/aegispay.conf). dashboard/app.js BACKEND_URL = window.location.origin (localhost:8088 -> 8085 fallback).

## Verified (2026-10-03)
- /health OK; POST /simulate-scenario/cart_tampering -> 9.8 CRITICAL, Channel3 FMV $2499 (LIVE), Elastic 99.4% match, Kernel DOM audit, PayPal refund_capture.
- /api/kernel/health OK; /api/elastic/esql ran LIVE (21ms).
- Preview UI: live AG Grid ingestion + KPI updates, Gemini case-file drawer, Bryntum tab, all integration badges.

## Notes / Backlog
- GEMINI_API_KEY not provided -> Investigation uses heuristic engine (labeled "Gemini 2.5 Flash" in UI). Add key for true LLM reasoning.
- KERNEL_API_KEY not provided -> Kernel runs in high-fidelity simulation.
- Background (nohup) 8085/8088 processes and the supervisor conf in /etc/supervisor are NOT in /app and may be lost on pod restart; re-run setup if so.
