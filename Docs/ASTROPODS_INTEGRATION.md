# Astropods Agent Deployment & Observability — AegisPay

## Overview

[Astropods](https://astropods.com) provides agent-native cloud infrastructure for packaging, deploying, and observing autonomous AI agents. 

In **AegisPay**, Astropods serves as the **declarative agent deployment harness**, defining the topology of our 4 specialized agents (Orchestrator, Investigation, Actuator, and Transaction Monitor) as an interconnected blueprint.

---

## 1. Why Astropods for AegisPay?

Deploying multi-agent systems with traditional tools (Kubernetes, Docker Swarm) introduces heavy infrastructure overhead. Astropods is built specifically for AI agents:

* **Declarative Agent Topology**: Defines agent roles, models (`gemini-2.5-flash`), tool interfaces, and A2A delegation trees in a single spec file (`astropods.yml`).
* **Versioned Blueprints**: Creates versioned deployment snapshots combining the container code, model instructions, and tool definitions.
* **Agent Observability**: Monitors A2A communication latency, decision token usage, and fraud mitigation frequency out-of-the-box.

---

## 2. Astropods Specification (`astropods.yml`)

The complete multi-agent blueprint is declared in the root [`astropods.yml`](../astropods.yml):

```yaml
version: "1.0"
project:
  name: "aegispay-fraud-defense"
  description: "Autonomous Multi-Agent AI system detecting and mitigating PayPal fraud in real time."

agents:
  - name: "orchestrator-agent"
    role: "Central Decision & Command Agent"
    runtime: "python:3.11"
    model:
      provider: "google"
      name: "gemini-2.5-flash"
    protocol:
      name: "a2a"

  - name: "investigation-agent"
    role: "Context Detective & Risk Reasoning Agent"
    model:
      provider: "google"
      name: "gemini-2.5-flash"
    tools:
      - name: "paypal_get_order_details"
      - name: "paypal_get_transaction_history"

  - name: "actuator-agent"
    role: "Policy Enforcement Officer"
    tools:
      - name: "paypal_refund_capture"
      - name: "paypal_void_authorization"

  - name: "transaction-monitor-agent"
    role: "Continuous Stream Monitor"
```

---

## 3. Deployment Workflow with Astropods CLI (`ast`)

Using the Astropods CLI, AegisPay can be validated, registered as a blueprint, and deployed in three steps:

### Step 1: Validate Specification
```bash
ast spec validate astropods.yml
```
*Confirms that agent models, tool endpoints, and port bindings adhere to the Astropods schema.*

### Step 2: Build & Push Versioned Blueprint
```bash
ast blueprint push aegispay-v1
```
*Builds the agent containers, packages model system prompts, and registers `aegispay-v1` in the Astropods private registry.*

### Step 3: Deploy Live Agent Swarm
```bash
ast blueprint deploy aegispay-v1 --env-file .env
```
*Provisions the 4 agents in the Astropods cloud, mounts the `GEMINI_API_KEY` and PayPal Sandbox credentials, and activates live A2A routing.*

---

## 4. Agent Observability in Astropods Dashboard

Once deployed, the Astropods control panel provides:
1. **A2A Execution Traces**: Inspects the sub-second handoff from `transaction-monitor` $\rightarrow$ `orchestrator` $\rightarrow$ `investigation` $\rightarrow$ `actuator`.
2. **LLM Cost & Token Monitoring**: Tracks Gemini 2.5 Flash token consumption per fraud case.
3. **Latency Benchmarks**: Validates that end-to-end investigation and refund execution remain under the $< 3.5\text{ s}$ SLA.
