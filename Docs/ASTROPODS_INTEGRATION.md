# Astropods Agent Deployment & Observability — AegisPay

## Overview

[Astropods](https://astropods.com) provides agent-native cloud infrastructure for packaging, deploying, and observing autonomous AI agents. 

In **AegisPay**, Astropods serves as the **declarative agent deployment harness**, defining the topology of our specialized agent swarm (Transaction Monitor, Orchestrator, Investigation, and Actuator) as an interconnected blueprint.

---

## 1. Why Astropods for AegisPay?

Deploying multi-agent systems with traditional tools (Kubernetes, Docker Swarm) introduces heavy infrastructure overhead. Astropods is built specifically for AI agents:

* **Declarative Agent Topology (`spec: blueprint/v1`)**: Defines agent roles, models (`gemini-2.5-flash`), tool interfaces, and PayPal integrations in a single spec file (`astropods.yml`).
* **Agent Cards (`AGENT.md`)**: Packages catalog metadata, tags, and architectural documentation for registry discovery.
* **Versioned Blueprints**: Creates versioned deployment snapshots combining the container code, model instructions, and tool definitions via `ast blueprint push`.
* **Agent Observability**: Monitors A2A communication latency, decision token usage, and fraud mitigation frequency out-of-the-box.

---

## 2. Astropods Specification (`astropods.yml`)

The complete multi-agent blueprint is declared in the root [`astropods.yml`](../astropods.yml):

```yaml
spec: blueprint/v1
name: aegispay-fraud-defense

agent:
  build:
    context: .
    dockerfile: Dockerfile
  interfaces:
    frontend: true
    messaging: true

models:
  gemini:
    provider: google
    models:
      - gemini-2.5-flash

providers:
  paypal:
    scope:
      - integrations
    variables:
      - name: CLIENT_ID
        datatype: string
        description: "PayPal Developer Sandbox Client ID"
      - name: CLIENT_SECRET
        datatype: string
        secret: true
        description: "PayPal Developer Sandbox Client Secret"
      - name: MODE
        datatype: string
        default: "sandbox"
        description: "PayPal API Mode (sandbox or live)"

integrations:
  paypal_commerce:
    provider: paypal

ingestion:
  paypal_fraud_webhook:
    container:
      build:
        context: .
        dockerfile: Dockerfile
      port: 8080
    trigger:
      type: webhook
```

---

## 3. Deployment Workflow with Astropods CLI (`ast`)

Using the Astropods CLI (`ast 0.27.0`), AegisPay is validated, registered as a blueprint, and deployed in three steps:

### Step 1: Validate Specification
```bash
ast spec validate -f astropods.yml
```
*Confirms that agent models, tool endpoints, and container bindings adhere to the Astropods schema:*
```text
Validating astropods.yml...
✓ astropods.yml is valid
```

### Step 2: Build & Push Versioned Blueprint
```bash
ast blueprint push aegispay-v1
```
*Builds the agent containers, packages model prompts, and registers `aegispay-v1` in the Astropods private registry.*

### Step 3: Deploy Live Agent Swarm
```bash
ast blueprint deploy aegispay-v1
```
*Provisions the agent swarm in the Astropods cloud, injects PayPal Developer Sandbox credentials, and activates live webhook listeners.*

---

## 4. Agent Observability in Astropods Dashboard

Once deployed, the Astropods control panel provides:
1. **A2A Execution Traces**: Inspects the sub-second handoff from `transaction-monitor` $\rightarrow$ `orchestrator` $\rightarrow$ `investigation` $\rightarrow$ `actuator`.
2. **LLM Cost & Token Monitoring**: Tracks Gemini 2.5 Flash token consumption per fraud case.
3. **Latency Benchmarks**: Validates that end-to-end investigation and refund execution remain under the $< 3.5\text{ s}$ SLA.

