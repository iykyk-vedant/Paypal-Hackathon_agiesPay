# AegisPay — 2-Minute Demo Video Walkthrough Script

**Format**: Screen recording (Loom / OBS) with voiceover  
**Recommended Duration**: 2 minutes to 2 minutes 30 seconds  
**Target Audience**: Devpost Judges (PayPal, AG Grid, Render, APIMatic, Astropods)

---

## 🎬 Video Recording Checklist

1. Launch AegisPay locally by double-clicking `run_demo.bat` (or starting the backend and opening `http://localhost:8088`).
2. Have your browser open at `http://localhost:8088` in full screen or clean window.
3. Have your terminal visible in split screen or ready to show real-time A2A logs.

---

## ⏱️ Step-by-Step Timestamped Script

### [0:00 – 0:25] Introduction & The Problem
* **On Screen**: Show the AegisPay GitHub README or Dashboard header.
* **Voiceover**:
  > *"Hi everyone, this is AegisPay — an autonomous multi-agent AI fraud shield built for PayPal Commerce and agentic commerce workflows.*
  > 
  > *As AI shopping agents and high-velocity digital checkouts expand, online merchants face a devastating dilemma: fraudulent account takeovers and card-testing bots cause catastrophic inventory loss and non-refundable chargeback fees, while blunt legacy filters cause high false declines for legitimate buyers.*
  > 
  > *AegisPay solves this by deploying a collaborative 4-agent swarm that monitors PayPal transactions, investigates risk with Gemini 2.5 Flash, and autonomously executes PayPal Payments v2 refunds and voids in sub-second latency before merchandise ever leaves the warehouse."*

---

### [0:25 – 1:00] Live Dashboard & Account Takeover Mitigation (Elasticsearch RAG)
* **On Screen**: Focus on the **AG Grid Enterprise** dashboard at `http://localhost:8088`. Point to the `● Backend Live (Port 8085)` badge and KPI counters. Click **`[Account Takeover ($4,850.00)]`**.
* **Voiceover**:
  > *"Here is the AegisPay Ops Center, powered by AG Grid Enterprise Quartz Dark with real-time Server-Sent Events.*
  > 
  > *Let's simulate a sophisticated Account Takeover attack. Watch what happens when I click Account Takeover:
  > In real time, the Transaction Monitor Agent ingests the PayPal order. The Orchestrator delegates the alert to our Investigation Agent, which combines Google Gemini 2.5 Flash with APIMatic OpenAPI rules and Elastic Cloud Serverless Vector Search.*
  > 
  > *Elasticsearch retrieves past attack #ATK-8812 with a 99.4% vector match, confirming this Tor proxy is part of a known syndicate. Scoring it a critical 9.4 out of 10, the Actuator Agent immediately fires a PayPal Payments v2 `refund_capture` call directly into the PayPal Developer Sandbox, neutralizing the fraud in under two seconds!"*

---

### [1:00 – 1:30] Channel3 Fair Market Value Shield & Elastic Drawer Inspection
* **On Screen**: Click **`[🏷️ Price Tampering ($149 vs $3,499)]`**. The transaction immediately appears in AG Grid as auto-refunded. Click the row to open the Gemini Case File Drawer, highlighting both the **Channel3 Product Intelligence card** and the **Elasticsearch Threat Intelligence & ES|QL card**.
* **Voiceover**:
  > *"Here's something revolutionary: we integrated Channel3's clean product API across 100M+ items to combat client-side DOM Cart Price Slashing.*
  > 
  > *Watch: an attacker manipulated their cart, buying a $3,499.00 Apple MacBook Pro for just $149.00.*
  > 
  > *In under a second, Channel3 verifies the true market value, detects the -95.7% variance, while Elasticsearch connects the signature to incident #EXP-9102 via ES|QL — executing an instant PayPal refund before the warehouse ships the computer!"*

---

### [1:30 – 1:55] Bryntum Dispute Horizon & Bot Mitigation
* **On Screen**: Switch to the **`[Bryntum Dispute Triage & Deadline Horizon]`** tab. Point out the interactive timeline, resources, and live dispute cards. Then switch back to AG Grid and trigger **`[Bot Burst ($1.28)]`**.
* **Voiceover**:
  > *"Clicking the Bryntum view switches to our interactive Dispute Triage & Deadline Horizon. Built on Bryntum Scheduler Stockholm Dark, it plots active dispute windows, evidence submission deadlines, and swarm workload across AI agents and human dispute specialists.*
  > 
  > *Next, triggering a Card Testing Bot attack executes an autonomous PayPal `void_authorization`, neutralizing the bot burst with zero human delay."*

---

### [1:55 – 2:15] Legitimate Purchases & CSV Compliance Export
* **On Screen**: Click **`[Normal Order ($45.00)]`**. Show it clearing instantly with a green badge (1.2/10). Then click **`[Export CSV]`** and show the downloaded CSV.
* **Voiceover**:
  > *"When an honest buyer purchases an item, AegisPay clears it in milliseconds with a risk score of 1.2 — ensuring zero friction for legitimate commerce.*
  > 
  > *Compliance teams can export audit-ready CSV logs instantly with AG Grid's native client-side export."*

---

### [2:15 – 2:35] Sponsor Integration Summary & Conclusion
* **On Screen**: Show the `render.yaml`, `astropods.yml`, `dashboard/bryntum-scheduler.js`, `channel3/client.py`, `elasticsearch/client.py`, and `.apimatic/` folders in VS Code or GitHub.
* **Voiceover**:
  > *"AegisPay delivers deep, native integration across all 8 hackathon platforms:
  > - PayPal Orders v2 & Payments v2 Sandbox REST API;
  > - AG Grid Enterprise Quartz Dark real-time surveillance;
  > - Elastic Cloud 9.6.0 Serverless vector search & ES|QL analytics;
  > - Bryntum Scheduler dispute triage & deadline horizon;
  > - Channel3 100M+ product catalog for cart price slashing detection;
  > - Render Infrastructure-as-Code Blueprint (`render.yaml`);
  > - APIMatic OpenAPI context plugin; and
  > - Astropods containerized multi-agent blueprint.*
  > 
  > *Thank you, and welcome to the future of autonomous merchant trust with AegisPay!"*
