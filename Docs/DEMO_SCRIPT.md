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

### [0:25 – 1:00] Live Dashboard & Account Takeover Mitigation
* **On Screen**: Focus on the **AG Grid Enterprise** dashboard at `http://localhost:8088`. Point to the `● Backend Live (Port 8085)` badge and KPI counters. Click **`[Account Takeover ($4,850.00)]`**.
* **Voiceover**:
  > *"Here is the AegisPay Ops Center, powered by AG Grid Enterprise Quartz Dark with real-time Server-Sent Events.*
  > 
  > *Let's simulate a sophisticated Account Takeover attack. Watch what happens when I click Account Takeover:
  > In real time, the Transaction Monitor Agent ingests the PayPal order. The Orchestrator delegates the alert to our Investigation Agent, which combines Google Gemini 2.5 Flash with APIMatic OpenAPI context rules.*
  > 
  > *Gemini detects an offshore Tor proxy, a 24x spending spike, and a cross-border destination mismatch, scoring it a critical 9.4 out of 10.*
  > 
  > *Because the score exceeds our safety threshold, the Actuator Agent immediately fires a PayPal Payments v2 `refund_capture` call directly into the PayPal Developer Sandbox, neutralizing the fraud in under two seconds!"*

---

### [1:00 – 1:30] Case File Inspection & Bot Mitigation
* **On Screen**: Click on the new high-risk row in the AG Grid table. The **Gemini AI Case File Drawer** smoothly slides in from the right. Then click **`[Bot Burst ($1.28)]`**.
* **Voiceover**:
  > *"Clicking any row opens the deep Gemini AI Case File. Merchants can inspect plain-English reasoning, specific risk factor tags, and the exact PayPal API transaction payload.*
  > 
  > *Next, let's trigger a Card Testing Bot attack. AegisPay catches the rapid microtransaction burst and disposable burner domain, and automatically executes a PayPal Payments v2 `void_authorization` — shutting down the bot without any manual human intervention required."*

---

### [1:30 – 1:55] Zero-Friction Legitimate Purchases & CSV Export
* **On Screen**: Click **`[Normal Order ($45.00)]`**. Show it clearing instantly with a green badge (1.2/10). Then click **`[Export CSV]`** and show the downloaded CSV.
* **Voiceover**:
  > *"When a legitimate verified buyer makes a purchase, AegisPay clears it in milliseconds with a risk score of 1.2 — ensuring zero friction for honest customers.*
  > 
  > *Fraud analysts can filter the entire surveillance stream and export audit-ready CSV reports with a single click via AG Grid's native export API."*

---

### [1:55 – 2:15] Sponsor Integration Summary & Conclusion
* **On Screen**: Show the `render.yaml`, `astropods.yml`, and `.apimatic/` folders in VS Code or GitHub.
* **Voiceover**:
  > *"AegisPay is production-ready across all 5 hackathon sponsor platforms:
  > - Direct PayPal Orders v2 and Payments v2 REST client with live sandbox credentials;
  > - High-performance AG Grid Enterprise Quartz Dark dashboard;
  > - One-click cloud deployment on Render via `render.yaml`;
  > - APIMatic OpenAPI context plugin for hallucination-free reasoning; and
  > - Astropods containerized agent blueprint.*
  > 
  > *Thank you, and welcome to the future of autonomous merchant trust with AegisPay!"*
