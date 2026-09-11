# 🏆 Devpost Project Submission: Supply Chain Supplier Status Check Agent

This document provides the complete, authoritative, and finalized text ready to copy-paste directly into the **Devpost Submission Form** for the **CALL-E "Your Code Is Calling" Hackathon (2026)**.

---

## 📌 Project Overview
- **Project Title**: Supply Chain Supplier Status Check Agent
- **Elevator Pitch / Tagline**: An autonomous 24/7 voice AI procurement specialist powered by CALL-E that proactively dials suppliers, diagnoses delivery delays, negotiates recovery timelines, and exports structured risk intelligence to ERP systems.
- **Submission Pull Request**: [CALLE-AI/awesome-phone-call-agents#440](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/440)
- **GitHub Repository**: [https://github.com/mohSadiq90/call-e-hackathon](https://github.com/mohSadiq90/call-e-hackathon)

---

## 🏷️ Built With (Devpost Tags — Up to 25 Tags)

### 📋 Comma-Separated (Single-Field Devpost Paste)
```text
python, calle-ai, voice-ai, telephony, mcp, model-context-protocol, pydantic, rest-api, webhooks, json-rpc, automation, supply-chain, procurement, logistics, erp-integration, natural-language-processing, conversational-ai, autonomous-agents, agentic-workflows, outbound-calling, tcpa-compliance, csv-export, json, cli, unit-testing
```

### 🔘 Space-Separated / Tag Pills
`python` `calle-ai` `voice-ai` `telephony` `mcp` `model-context-protocol` `pydantic` `rest-api` `webhooks` `json-rpc` `automation` `supply-chain` `procurement` `logistics` `erp-integration` `natural-language-processing` `conversational-ai` `autonomous-agents` `agentic-workflows` `outbound-calling` `tcpa-compliance` `csv-export` `json` `cli` `unit-testing`

### 🏗️ Detailed 25 Tags Rationale

| # | Tag | Role in Project |
|---|---|---|
| 1 | `python` | Core language (Python 3.12+) driving SDK client, CLI runner, parsers, and test suites. |
| 2 | `calle-ai` | Official CALL-E telephony and voice AI integration platform (`calle-ai` package). |
| 3 | `voice-ai` | Natural voice generation and speech-to-text processing for human-sounding vendor calls. |
| 4 | `telephony` | Outbound PSTN phone call orchestration with carrier-grade reliability. |
| 5 | `mcp` | Model Context Protocol implementation exposing procurement agent tools. |
| 6 | `model-context-protocol` | Official MCP stdio standard for LLM and agent orchestration. |
| 7 | `pydantic` | Typed data modeling, validation schemas, and automated financial risk calculations. |
| 8 | `rest-api` | Telephony dispatch and external system integration endpoints. |
| 9 | `webhooks` | Asynchronous call event handling and transcript delivery. |
| 10 | `json-rpc` | Protocol for standard input/output MCP tool invocation. |
| 11 | `automation` | Autonomous scheduling, bulk dialing, and robotic process automation. |
| 12 | `supply-chain` | Domain application targeting global inventory, manufacturing, and fulfillment pipelines. |
| 13 | `procurement` | Enterprise purchase order management and vendor compliance verification. |
| 14 | `logistics` | Freight tracking, freight surcharges, and port/customs delay mitigation. |
| 15 | `erp-integration` | Direct compatibility with SAP S/4HANA, Oracle NetSuite, and Walmart Retail Link. |
| 16 | `natural-language-processing` | Entity extraction, currency detection, and date normalization from unstructured speech. |
| 17 | `conversational-ai` | Deterministic 5-step conversational protocol guiding structured business dialogues. |
| 18 | `autonomous-agents` | Independent decision-making agents executing follow-ups without manual intervention. |
| 19 | `agentic-workflows` | Multi-step task composition: check status -> diagnose root cause -> negotiate -> report. |
| 20 | `outbound-calling` | Proactive outbound calling to supplier fulfillment managers prior to critical deadlines. |
| 21 | `tcpa-compliance` | Built-in legal disclosure ("calling on a recorded line") and compliance safeguards. |
| 22 | `csv-export` | Automated generation of ERP-ready `procurement_status_report.csv` spreadsheets. |
| 23 | `json` | Structured JSON audit ledger (`procurement_status_report.json`) for data pipelines. |
| 24 | `cli` | Interactive command-line interface (`main.py`) with batch and single-supplier modes. |
| 25 | `unit-testing` | 100% test pass rate (15/15 unit tests) across all models, parsers, and pipelines. |

---

## 📝 Devpost Project Story (Copy & Paste Ready)

### 🎯 Inspiration
In modern retail and enterprise supply chains (e.g., automotive manufacturing, aerospace, large-scale retail like Walmart), procurement teams lose **2 to 3 hours per manager every single day** manually dialing vendors across multiple timezones just to verify if critical purchase orders will arrive on schedule. 

When delivery delays are discovered late, assembly lines stall, retail shelves sit empty (stockouts), and emergency air freight surcharges skyrocket. We built the **Supply Chain Supplier Status Check Agent** to turn manual, tedious vendor follow-ups into an autonomous voice AI operation—proactively verifying fulfillment, diagnosing root causes, quantifying financial penalties, and alerting procurement leads before costly disruptions hit the factory floor.

---

### ⚙️ What It Does
The agent acts as an autonomous 24/7 procurement voice specialist that:
- **Autonomous Outbound Telephony**: Dials supplier dispatchers prior to committed delivery deadlines using the CALL-E platform.
- **Deterministic 5-Step Conversational Protocol**:
  1. **Greeting & Verification**: Identifies itself as Enterprise Procurement on a recorded line and verifies dispatcher credentials.
  2. **Fulfillment Status Check**: Executes a binary schedule check against committed PO delivery dates and quantities.
  3. **Delay Root Cause Analysis**: Categorizes bottlenecks (`RAW_MATERIAL_SHORTAGE`, `LOGISTICS_PORT_CONGESTION`, `QUALITY_CONTROL_HOLD`, `PRODUCTION_HALT`, etc.).
  4. **Revised Timeline & Mitigation**: Negotiates confirmed arrival dates and explores partial shipments or expedited air freight.
  5. **Cost Impact & Escalation**: Quantifies financial SLA penalty exposure, captures escalation supervisor contacts, and confirms closure.
- **Structured Intelligence Extraction**: Parses unstructured voice transcripts into typed Pydantic data models.
- **Enterprise Reporting**: Outputs real-time ASCII executive dashboards, ERP-ready CSV reports (`procurement_status_report.csv`), and JSON audit ledgers (`procurement_status_report.json`).
- **Multi-Modal Integration**: Operates across 5 modalities: Python SDK, REST API/Webhooks, CLI (`main.py`), Reusable Agent Skill (`skills/supply-chain-agent/SKILL.md`), and Model Context Protocol (`src/mcp_server.py`).

---

### 🛠️ How We Built It
- **Telephony & Voice AI**: Integrated the official CALL-E Python SDK (`calle-ai`) with a dual-mode engine supporting both live outbound calling and a zero-credit high-fidelity offline simulator.
- **Conversational State Machine**: Designed deterministic prompts (`prompts/supplier_agent_prompt.py`) adhering strictly to enterprise procurement workflows and TCPA disclosure compliance.
- **Data Modeling & Validation**: Implemented robust Pydantic schemas in `src/models.py` (`Supplier`, `PurchaseOrder`, `CallResult`, `BatchProcurementReport`) with automated financial exposure calculations (daily penalty rate $\times$ delay days $+$ freight surcharges).
- **Transcript & Entity Parser**: Built a multi-pass regex and NLP pattern extractor in `src/transcript_parser.py` to isolate dates, currency amounts, contact info, and standardized root-cause taxonomy.
- **Model Context Protocol (MCP)**: Implemented a production JSON-RPC 2.0 stdio MCP server (`src/mcp_server.py`) exposing `calle_check_supplier_status` and `calle_run_batch_procurement` for autonomous agent orchestration.
- **Testing Suite**: Built a comprehensive automated test suite (`tests/`) verifying models, parsers, pipelines, and MCP protocols with **15/15 unit tests passing (100% pass rate)**.

---

### 🚧 Challenges We Ran Into
- **Conversational Ambiguity in Live Logistics Calls**: Suppliers rarely speak in structured data. They hedge dates, mention ambiguous logistical hurdles ("adhesive resin stuck at the port"), or offer split shipments. We designed a multi-pass transcript parser and strict conversation branches to normalize ambiguous natural language into typed enums and dates.
- **API Credit Constraints During Development**: With free tiers limited to 20 calls, iterating on complex edge cases could rapidly exhaust credits. We built a zero-credit high-fidelity simulation engine that replicates real dispatcher dialogue, allowing comprehensive end-to-end testing and CI verification without burning live credits.
- **Decoupled Multi-Modal Architecture**: Designing the agent to run identically across a standalone CLI, an automated batch runner, a reusable Agent Skill manifest, and an MCP server required strict separation of concerns between telephony dispatch, conversation logic, and data ingestion.

---

### 🏆 Accomplishments That We're Proud Of
- **Official Pull Request Submitted**: Successfully opened Pull Request **#440** to the official [`CALLE-AI/awesome-phone-call-agents`](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/440) repository with 100% validation check pass rate.
- **15/15 Automated Unit Tests Passing**: Full test coverage across models, transcript parsing, batch reporting, and MCP tools.
- **5 Supported Integration Modalities**: Shipped complete support for Python SDK, Webhook API, CLI, Agent Skill, and MCP Server in a single repo.
- **Zero-Credit Simulator**: Built a realistic testing engine enabling any developer to clone the repo and run simulated supplier batches out of the box.
- **Actionable Financial Risk Quantification**: Instead of just returning call audio, the system translates conversations directly into dollar-denominated financial risk metrics for procurement leaders.

---

### 💡 What We Learned
- **Enterprise Voice AI Demands Determinism**: Open-ended chatbots can wander off topic, but supply chain voice operations require deterministic conversational gates (identity validation, binary confirmations, supervisor escalation) to yield clean, actionable business data.
- **The Power of Model Context Protocol (MCP)**: Exposing phone calling capabilities over MCP enables autonomous LLM agents to trigger real-world phone calls and parse vendor intelligence as easily as querying a database.
- **Simulation-First Development**: Telephony APIs have latency, cost, and human dispatcher dependencies. Building a mock simulation harness first dramatically accelerated our velocity.

---

### 🔮 What's Next for Supply Chain Supplier Status Check Agent
- **Direct ERP / EDI Two-Way Connectors**: Native bi-directional synchronization with SAP S/4HANA, Oracle NetSuite, and Walmart Retail Link to auto-trigger calls 48 hours prior to purchase order milestones.
- **Inbound Callback & Re-negotiation Line**: Dedicated phone numbers allowing vendor dispatchers to call back with updated tracking numbers, automatically updating the procurement ledger.
- **Multilingual Voice Support**: Expanding CALL-E voice models to support multilingual suppliers (Spanish, Mandarin, Vietnamese, German) for global cross-border procurement.
- **Autonomous Alternate Sourcing**: If a primary supplier reports a critical delay (>7 days), automatically trigger secondary supplier availability calls and suggest inventory re-routing to prevent assembly line stoppages.
