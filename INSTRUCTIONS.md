# 📋 CALL-E Hackathon Guidelines & Implementation Instructions

This document provides the complete, authoritative operational instructions and submission requirements for the **CALL-E "Your Code Is Calling" Hackathon (2026)**, specifically tailored to the **Supply Chain Supplier Status Check Agent**.

---

## 🏁 1. Get Started Workflow

### Step 1: Install CALL-E & Sign In (5 min)
1. **Account Registration**:
   - Register for a CALL-E account at [https://calle.ai](https://calle.ai) (or follow the official onboarding guide).
   - Every new CALL-E account automatically receives **20 free calls** upon registration.
2. **API Key Generation**:
   - Navigate to the CALL-E Developer Console.
   - Generate your live API Key (`calle_live_...`) and note your designated Agent ID.
   - Store these in your local `.env` configuration (see [Environment Setup](#environment-configuration)).
3. **Request Additional Calls**:
   - 20 calls may be consumed rapidly during development and demonstration recordings.
   - If running low on call credits, submit the official **CALL-E Additional Calls Request Form** to top up development credits before final recording.

---

### Step 2: Integration Modalities (~30 min)
CALL-E supports five primary connection vectors. This repository provides implementations across all 5 modalities:

| Modality | Description | Implementation in this Repository |
| :--- | :--- | :--- |
| **SDK** | Direct programmatic control via Python SDK (`calle-ai`) | [`src/calle_client.py`](src/calle_client.py) (`CalleClient`) |
| **API** | REST/Webhook endpoints for dispatch and callback | CALL-E telephony webhook dispatch in `src/calle_client.py` |
| **MCP** | Model Context Protocol server exposing tool definitions for AI agents | [`src/mcp_server.py`](src/mcp_server.py) (`calle_check_supplier_status`) |
| **CLI** | Standalone interactive command-line interface | [`main.py`](main.py) with batch & single-supplier flags |
| **SKILL** | Reusable Antigravity / AI Agent Skill manifest | [`skills/supply-chain-agent/SKILL.md`](skills/supply-chain-agent/SKILL.md) |

---

### Step 3: Browse Example Skills & Brainstorm (30 min)
- Review existing reference agents in [`CALLE-AI/awesome-phone-call-agents`](https://github.com/CALLE-AI/awesome-phone-call-agents).
- **Our Selected Use Case**: Enterprise Supply Chain Vendor Fulfillment & Escalation Agent.
  - **Problem**: Procurement managers spend 2-3 hours/day manually calling suppliers across timezones to verify order fulfillment.
  - **Solution**: Autonomous outbound phone agent calls suppliers, verifies deadlines, isolates root causes for delays, assesses penalty risks, and outputs clean CSV/JSON dashboards directly to ERP systems.

---

## 🎯 2. Requirements: What to Build

### Core Scope
1. **Impactful Business Use Case**:
   - Real-world enterprise domain (Procurement & Supply Chain Operations).
   - Measurable ROI: Replaces 2+ hours of manual phone checks per manager per day and captures critical delivery slippages before factory stoppages occur.
2. **Deterministic 5-Step Conversational Protocol**:
   - **Step 1: Greeting & Verification**: Dispatcher identity confirmation on a recorded line.
   - **Step 2: Fulfillment Status Check**: Binary schedule check against committed PO date and volume.
   - **Step 3: Root Cause Analysis**: Identifies failure category (`RAW_MATERIAL_SHORTAGE`, `PORT_CONGESTION`, `QUALITY_HOLD`, `EQUIPMENT_BREAKDOWN`).
   - **Step 4: Revised Timeline & Mitigation**: Negotiates revised arrival date and partial shipment options.
   - **Step 5: Financial Impact & Escalation**: Calculates daily delay penalties, expedited air freight costs, captures supervisor contact, and confirms closure.
3. **Structured Intelligence Output**:
   - Automatically parses unstructured call transcripts into typed Pydantic models.
   - Exports ERP-ready CSV (`procurement_status_report.csv`) and JSON ledger (`procurement_status_report.json`).
4. **Zero-Credit Mock Simulation Engine**:
   - Built-in fallback simulator allows comprehensive testing, integration verification, and demo runs without burning live phone credits.

---

## 📦 3. What to Submit: Deliverables & Submission Checklist

### A. Pull Request to Public Repository
- **Target Repository**: [`https://github.com/CALLE-AI/awesome-phone-call-agents`](https://github.com/CALLE-AI/awesome-phone-call-agents)
- **Target Branch**: `main`
- **Submission Pull Request**: [`https://github.com/CALLE-AI/awesome-phone-call-agents/pull/440`](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/440)
- **PR Status**: **Open & Verified** (Title: `feat(skills): add supply-chain-supplier-status skill and enterprise application entry`)
- **Contribution Area Selection**:
  - `Agent Skills` -> Add skill entry linking to `skills/supply-chain-supplier-status/`
  - `Enterprise Apps` -> Add entry linking to `https://github.com/mohSadiq90/call-e-hackathon`

### B. Devpost Submission Form Requirements
1. **Pull Request URL**: [`https://github.com/CALLE-AI/awesome-phone-call-agents/pull/440`](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/440)
2. **Demonstration Video (~3 minutes)**:
   - Must be uploaded to **YouTube** or **Vimeo** and set to **Public** or **Unlisted** (publicly viewable).
   - **Video Structure (3-Minute Script)**:
     - `0:00 - 0:45`: The Problem (Supply chain delays, manual phone calls, hours wasted).
     - `0:45 - 1:45`: Live / Simulated Agent Calls:
       - Supplier 1 (Apex Microelectronics): On-time fulfillment.
       - Supplier 2 (Pacific Packaging): 5-day delay due to raw material shortage, partial shipment negotiated, expedited freight costs captured.
     - `1:45 - 2:30`: Dashboard & Structured Intelligence (Live console output, CSV/JSON export, automated penalty calculations).
     - `2:30 - 3:00`: Architecture (CALL-E SDK/MCP integration, Pydantic data pipelines, test coverage).
3. **CALL-E Account Email**:
   - The registered email address associated with your active CALL-E developer account.
4. **Project GitHub URL**:
   - `https://github.com/mohSadiq90/call-e-hackathon`
5. **Optional Demo URL**:
   - Interactive demo or dashboard web URL if deployed.
6. **CALL-E Feedback Survey**:
   - Complete the official survey for eligibility in the $1,000 Most Valuable Feedback Prize Pool (5 x $200).

---

## 🛠️ 4. Local Execution & Quick Reference

```bash
# 1. Clone repository
git clone https://github.com/mohSadiq90/call-e-hackathon.git
cd call-e-hackathon

# 2. Install dependencies in /tmp or virtual environment
pip install -r requirements.txt

# 3. Run all automated unit tests (100% pass rate)
python3 -m unittest discover -s tests -v

# 4. Execute CLI with default mock simulation
python3 main.py

# 5. Run single supplier test
python3 main.py --supplier SUP-102

# 6. Run live telephony (requires live API key in .env)
python3 main.py --live --company-name "Walmart Global Procurement"

# 7. Start Model Context Protocol (MCP) Server
python3 src/mcp_server.py
```
