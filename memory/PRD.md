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
- GEMINI_API_KEY added to /app/.env (2026-10-03) -> Investigation attempts true LLM reasoning, gracefully falls back to heuristic engine on failure.
- KERNEL_API_KEY not provided -> Kernel runs in high-fidelity simulation.
- Background (nohup) 8085 orchestrator process and the supervisor conf in /etc/supervisor are NOT in /app and may be lost on pod restart; re-run setup if so (process id changes each restart — check `ps aux | grep orchestrator`).
- AG Grid Enterprise license key is a trial/invalid key -> cosmetic watermark in console (P2, not fixed, not requested yet).

## Enterprise Dashboard Refactor (2026-10-03)
Refactored `dashboard/` from hackathon-demo styling into a production B2B Fraud Ops Surveillance Center (Stripe Radar / Datadog SIEM aesthetic). Zero breaking changes — all existing element IDs/bindings preserved.
- Removed all "hackathon/prize" references (index.html, style.css, bryntum-scheduler.js). Header badges -> `.subsystem-telemetry-bar` (7 live sys-badges w/ colored health dots: PayPal, AG Grid, Bryntum, Channel3, Elastic, KERNEL, Zapier).
- Live status pill: added latency badge (`SSE Live • Nms latency`) + heartbeat dot animation.
- KPI cards: removed all hardcoded vanity numbers. `computeInitialKpiState()` derives Total Volume / Transactions / Fraud Intercepted / Attack Count from `INITIAL_TRANSACTIONS.reduce()`. Decision Latency (P90) computed live from `kpiState.latencySamples` (measured via `performance.now()` around each scenario trigger -> SSE response). Micro-counter flash animation on update.
- `INITIAL_TRANSACTIONS[].rawJson` restructured to authentic PayPal Orders v2 schema (id/intent/payer/purchase_units/links) + sibling `aegispay_decision`. Added `captureId`/`ipCountry`/`isoTimestamp` fields per tx for evidence generation.
- Segmented risk triage filter bar (All/Critical ≥7.0/Review 4-6.9/Safe <4.0) wired via AG Grid `isExternalFilterPresent`/`doesExternalFilterPass`.
- Quick filter upgraded: clear button + `getQuickFilterText` on Customer/RiskScore columns to also match email, payer ID, risk factors.
- Case File modal: added "Copy Dispute Evidence Package" button -> `generateDisputeEvidencePackage(tx)` builds a 6-section Markdown brief (meta, Channel3 FMV, KERNEL DOM audit, Elastic intel, Zapier MCP actions, Gemini justification), copied via clipboard + custom toast ("PayPal Resolution Center dispute package copied to clipboard!").
- AG Grid live row insertion: `insertRowWithGlow()` + `rowClassRules` flash green/red border-glow for 1.8s on new safe/fraud rows (replaces plain `applyTransaction`).
- Glassmorphism polish on kpi/grid/terminal/modal cards, radial-gradient obsidian background, modal slide-in animations.
- Bryntum: removed hackathon comment, rebranded header, added 3 milestone events (Evidence Assembled / Merchant Ops Review / PayPal Resolution Center SLA Deadline) to the 10-day dispute horizon.
- Backend (`orchestrator_agent/agent.py`, `paypal/client.py`): enriched `final_record` with `capture_id`, `ip_country` (from shipping/payer country), guaranteed ISO `timestamp` — consumed by the new Dispute Evidence Package generator for live SSE transactions.
- GEMINI_API_KEY added to `.env` per user-provided key; existing try/except fallback to heuristic engine unchanged (handles invalid/expired key gracefully).
- Self-tested: curl on `/simulate-scenario/cart_tampering` confirms `capture_id`/`ip_country`/`timestamp` present; screenshot confirms dashboard renders with correct dynamically-computed KPIs ($10,666.50 volume / 6 tx / $8,050.00 fraud / 2 attacks matching `INITIAL_TRANSACTIONS` math) and no console errors from app.js. Could not interactively verify modal/filter clicks via the screenshot tool in this session (tool returned a static pre-interaction frame); logic was verified by code review instead.
