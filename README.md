# 📞 CALL-E Autonomous Supply Chain Telephony Agent 📦📞

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Passing](https://img.shields.io/badge/Tests-76%2F76%20Passing-brightgreen.svg)]()
[![CALL-E SDK](https://img.shields.io/badge/Telephony-CALL--E%20SDK-purple.svg)](https://calle.ai)

> **Autonomous phone agent that dials suppliers to verify purchase order fulfillment by deadline, captures delay root causes, estimates financial risk, and outputs structured intelligence directly into procurement dashboards.**

---

## 🎯 Executive Summary & Pitch

In modern retail and enterprise supply chains (e.g. Walmart, automotive manufacturing, aerospace), procurement teams lose **2 to 3 hours per manager per day** manually dialing suppliers across multiple timezones to verify whether critical purchase orders will arrive on schedule. When delays are discovered late, assembly lines stall, stockouts occur, and emergency freight costs skyrocket.

The **CALL-E Supply Chain Supplier Status Check Agent** automates this entire operational bottleneck:
1. **Dials suppliers autonomously** prior to committed delivery milestones.
2. **Executes a deterministic 5-step conversational protocol** (greeting $\to$ fulfillment check $\to$ delay reason $\to$ revised timeline $\to$ financial impact & escalation).
3. **Extracts structured procurement intelligence** (fulfillment status, revised dates, root cause category, expedited freight costs, escalation contacts).
4. **Aggregates batch results** into an executive dashboard, calculating SLA financial penalties and highlighting critical escalations in CSV and JSON formats.

---

## 🏗️ Architecture & 5-Step Conversation Flow

```
                      ┌─────────────────────────────────────────┐
                      │    Purchase Orders (ERP / CSV / JSON)   │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │   CALL-E Autonomous Outbound Dialer     │
                      └────────────────────┬────────────────────┘
                                           │
               ┌───────────────────────────┴───────────────────────────┐
               ▼                                                       ▼
  [ 1. Greeting & Identity ]                              [ Live CALL-E SDK Telephony ]
               │                                                       │
               ▼                                                       ▼
  [ 2. Fulfillment Status Check ]                         [ Speech-to-Text Transcription ]
        │               │                                              │
     (On-Time)      (Delayed)                                          ▼
        │               │                                 [ Structured Regex & Entity  ]
        │               ▼                                 [       Parser Engine        ]
        │     [ 3. Root Cause Analysis ]                               │
        │               │                                              ▼
        │               ▼                                 ┌────────────────────────────┐
        │     [ 4. Revised Timeline &  ]                  │ Executive Risk Dashboard   │
        │     [     Mitigation Options ]                  │ • CSV (ERP / Retail Link)  │
        └───────┬───────┘                                 │ • JSON Procurement Ledger  │
                │                                         │ • Terminal Alert Summary   │
                ▼                                         └────────────────────────────┘
  [ 5. Cost Impact & Escalation ]
```

### The 5 Conversational Steps:
1. **Greeting & Verification**: Introduces agent as Enterprise Procurement Operations on a recorded line; verifies dispatcher identity.
2. **Fulfillment & Deadline Check**: Performs a binary status check against committed delivery dates and order quantities.
3. **Delay Root Cause (Conditional)**: If behind schedule, categorizes supply chain failure (Raw Material Shortage, Quality Control Hold, Port/Rail Congestion, Equipment Breakdown).
4. **Revised Timeline & Mitigation**: Negotiates guaranteed arrival date and investigates partial shipments or air freight.
5. **Cost Impact & Escalation**: Records expedited freight surcharges, calculates estimated financial delay exposure, captures escalation supervisor details, and confirms the ticket.

---

## 🚀 Quickstart & Setup

### 1. Clone & Install
```bash
git clone https://github.com/mohSadiq90/call-e-hackathon.git
cd call-e-hackathon

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the `.env.example` template:
```bash
cp .env.example .env
```
Configure your keys in `.env`:
```ini
CALLE_API_KEY=calle_live_your_api_key_here
CALLE_AGENT_ID=supplier-status-checker-v1
DEFAULT_DAILY_DELAY_PENALTY_USD=1500.0
ENABLE_MOCK_SIMULATOR=true
```

> **Note**: If `CALLE_API_KEY` is omitted, the client automatically defaults to **high-fidelity simulation mode**, allowing complete end-to-end testing with zero API credit consumption!

---

## 💻 CLI Usage

### Run Simulation Batch (Default Test Dataset)
```bash
python3 main.py
```

### Target a Specific Supplier
```bash
python3 main.py --supplier SUP-102
```

### Run Live Telephony via CALL-E SDK
```bash
python3 main.py --live --company-name "Walmart Global Procurement"
```

### Custom Dataset & Custom Output Directory
```bash
python3 main.py --data data/suppliers.json --output-dir /tmp/procurement_reports
```

### Run Simulation Batch & Launch Web Dashboard
```bash
python3 main.py --web
```

### Launch Standalone Web Dashboard Server
```bash
python3 -m src.server --port 8000
```
Then navigate to `http://localhost:8000` in your web browser.

---

## 🌐 Interactive Web Dashboard & REST API

The CALL-E Supply Chain Intelligence platform includes an enterprise operations dashboard and RESTful API backend ([`src/server.py`](src/server.py) and [`src/html_dashboard.py`](src/html_dashboard.py)).

### Key Dashboard Capabilities:
1. **Executive Control Tower**:
   - Live KPI metrics: Total Calls Executed, On-Time Fulfillment %, Delay Disruptions Count, Total Financial Exposure ($), Critical Escalations, and Autonomous Voice Hours Saved.
2. **Visual Analytics & Taxonomy Breakdown**:
   - Status distribution breakdown across all purchase orders.
   - Root cause categorization (`RAW_MATERIAL_SHORTAGE`, `LOGISTICS_PORT_CONGESTION`, `QUALITY_CONTROL_HOLD`, `PRODUCTION_HALT`, etc.).
   - Risk distribution segmented across supply lines.
3. **Interactive Multi-Filter & Search Engine**:
   - Quick-filter pills: All, On-Time, Delayed, Partial Dispatch, Unreachable, and Escalations Only.
   - Category dropdown filter, sorting (Highest Financial Risk, Longest Delay, Date, Vendor Name).
   - Real-time instant text search across PO numbers, vendor names, line items, and contacts.
4. **Dual Display Modalities**:
   - **Data Table View**: High-density operational table with status badges and risk calculations.
   - **Cards Grid View**: Card-based visual overview.
5. **Call Inspection & Real Telephony Audio Player Modal**:
   - Full conversational transcript bubble visualization.
   - HTML5 `<audio>` player with live waveform scrubbing, variable playback rates (1.0x, 1.25x, 1.5x, 2.0x), and live verified recording badges.
   - High-fidelity fallback audio simulation for offline and mock demonstration records.
   - Direct escalation contact card with clickable phone and email.
6. **On-Demand Outbound Call Trigger**:
   - Trigger new autonomous verification calls directly from the browser UI or REST API.
7. **Offline Standalone Support**:
   - The generated [`output/procurement_dashboard.html`](output/procurement_dashboard.html) is completely self-contained and can be opened directly as a static file (`file:///...`) with full interactivity, client-side fallback simulation, and CSV/JSON export.

### REST API Endpoints:
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the interactive executive HTML operations dashboard |
| `GET` | `/health`, `/api/health` | Health check endpoint returning loaded call count |
| `GET` | `/api/summary` | Executive KPI aggregates and procurement status report |
| `GET` | `/api/calls` | Query call records with filters (`?status=`, `?category=`, `?escalation_only=`, `?search=`, `?recording_only=`) |
| `GET` | `/api/calls/{call_id}` | Detailed call record with conversational transcript |
| `GET` | `/api/calls/{call_id}/audio` | Stream telephony call audio (WAV) directly for in-browser playback |
| `GET` | `/api/calls/{call_id}/recording` | Retrieve CALL-E recording metadata and stream link |
| `POST` | `/api/calls/trigger` | Trigger outbound verification call (live or simulated) |
| `GET` | `/api/export/csv` | Stream latest ERP-ready CSV report |
| `GET` | `/api/export/json` | Stream latest machine-readable JSON report |
| `GET` | `/api/db/stats` | Real-time SQLite storage statistics and record counts |
| `POST` | `/api/reload` | Recompute or switch dataset on demand |

---

## 📊 Live Output & Executive Dashboard

When executed, the agent prints a real-time executive dashboard and outputs clean CSV, JSON, and HTML ledgers:

```text
================================================================================
  CALL-E AUTONOMOUS PROCUREMENT AGENT - DAILY STATUS REPORT
  Generated: 2026-09-11T11:36:15Z | Report ID: rep_a128967e
================================================================================

📊 EXECUTIVE KPI SUMMARY:
  • Total Purchase Orders Checked : 5
  • On-Time Fulfillment           : 2 (40.0%)
  • Delayed / At-Risk Shipments   : 3
  • Unreachable Vendors           : 0
  • Total Estimated Financial Risk: $33,450.00
  • Critical Escalations Required : 3

--------------------------------------------------------------------------------
ORDER ID   | SUPPLIER               | STATUS    | ORIG DATE  | REV DATE   | DELAY | RISK ($)  
--------------------------------------------------------------------------------
PO-91042   | Apex Microelectronic.. | ✅ ON_TIME | 2026-09-18 | 2026-09-18 | 0d    | $0        
PO-88120   | Pacific Packaging So.. | ⚠️ DELAYED | 2026-09-15 | 2026-09-20 | +5d   | $8,350    
PO-74211   | Global Precision Mac.. | ⚠️ DELAYED | 2026-09-16 | 2026-09-22 | +6d   | $11,200   
PO-62005   | Metro Fasteners & In.. | ✅ ON_TIME | 2026-09-14 | 2026-09-14 | 0d    | $0        
PO-51980   | Zenith Hydraulics & .. | ⚠️ DELAYED | 2026-09-17 | 2026-09-24 | +7d   | $13,900   
--------------------------------------------------------------------------------

🚨 CRITICAL ESCALATION ACTION REQUIRED:
  • Order PO-88120 (Pacific Packaging Solutions):
    - Delay: 5 days (New Target: 2026-09-20)
    - Root Cause: RAW_MATERIAL_SHORTAGE (Polymer resin adhesive shipment delayed at port)
    - Expedited Freight: $850.00 | Total Risk: $8,350.00
    - Escalation Lead: Maria Gomez (+1-555-014-9923)
```

---

## 🧪 Automated Testing

A comprehensive test suite covers models, transcript parsing, SQLite database persistence, MCP server, HTML dashboard rendering, and FastAPI REST endpoints:

```bash
python3 -m unittest discover -s tests
```

Output:
```text
Ran 76 tests in 0.533s

OK
```

---

## 🌐 Public Hostinger VPS Hosting (`calle.fyro.cloud`)

The platform includes automated deployment configurations and scripts for hosting on a **Hostinger VPS** with SSL under `calle.fyro.cloud` (or any subdomain of `fyro.cloud`):
- **Live Mission Control Portal**: Executive operations dashboard with real-time KPI tracking.
- **Workflow Trigger Center**: Single-click dispatch of live phone calls via CALL-E or instant simulation, plus batch verification runner across supplier categories.
- **Automated Deployment**: Ready-to-run 1-command installer script in [`deploy/deploy_hostinger.sh`](deploy/deploy_hostinger.sh) and Docker Compose setup.
- **Full Architecture Plan**: Detailed deployment guide and DNS configuration in [`docs/HOSTINGER_VPS_DEPLOYMENT_PLAN.md`](docs/HOSTINGER_VPS_DEPLOYMENT_PLAN.md).

---

## 📁 Repository Structure

```
call-e-hackathon/
├── README.md                      # Complete project documentation & pitch
├── INSTRUCTIONS.md                # Hackathon guidelines, build specs & submission instructions
├── PROGRESS.md                    # Project work log and sprint tracker
├── pyproject.toml                 # Package configuration
├── requirements.txt               # Dependencies (pydantic, fastapi, uvicorn, calle-ai)
├── .env.example                   # Environment configuration template
├── config/
│   ├── __init__.py
│   └── settings.py                # Environment configuration loader
├── deploy/                        # Production deployment configuration for Hostinger VPS
│   ├── Dockerfile                 # Multi-stage production container build
│   ├── docker-compose.yml         # Container orchestration
│   ├── calle.service              # Systemd unit service configuration
│   ├── deploy_hostinger.sh        # 1-command automated VPS deploy script
│   ├── .env.production.example    # Production environment variable template
│   └── nginx/
│       └── calle.fyro.cloud.conf  # Nginx reverse proxy & Let's Encrypt SSL config
├── docs/
│   ├── CALL_E_CREDITS_BLURB.md    # Official 2-3 sentence blurb for additional CALL-E credits
│   ├── DEVPOST_SUBMISSION.md      # Authoritative copy-paste text for Devpost submission
│   └── HOSTINGER_VPS_DEPLOYMENT_PLAN.md # Full VPS architecture & workflow plan

├── prompts/
│   ├── __init__.py
│   ├── supplier_agent_prompt.py   # 5-step conversation flow & system instructions
│   └── system_instructions.md     # Markdown conversation tree reference
├── skills/
│   └── supply-chain-agent/
│       └── SKILL.md               # Reusable Antigravity / AI Agent Skill manifest
├── scripts/
│   └── generate_enterprise_data.py # 52-supplier enterprise dataset generator
├── src/
│   ├── __init__.py
│   ├── models.py                  # Pydantic schemas (PO, Supplier, CallResult)
│   ├── database.py                # SQLite persistence manager (WAL mode, indexes, CRUD)
│   ├── calle_client.py            # CALL-E SDK client + High-fidelity simulator
│   ├── transcript_parser.py       # Deterministic extraction of dates, costs, causes
│   ├── reporter.py                # CSV, JSON, ASCII, and HTML dashboard generator
│   ├── html_dashboard.py          # Interactive single-page executive web dashboard
│   ├── server.py                  # FastAPI HTTP backend & REST API server
│   └── mcp_server.py              # Model Context Protocol (MCP) tool server
├── data/
│   ├── suppliers.json             # 5 realistic test supplier records & scenarios
│   ├── suppliers.csv              # CSV format for ERP batch ingestion
│   ├── suppliers_enterprise_50.json # 52 enterprise Fortune 500 supplier dataset
│   └── suppliers_enterprise_50.csv  # 52 enterprise supplier CSV export
├── output/
│   ├── procurement_status_report.csv  # Structured ERP delivery ledger
│   ├── procurement_status_report.json # Full audit trail & structured intelligence
│   ├── procurement_dashboard.html     # Interactive single-page executive dashboard
│   └── procurement_telephony.db       # SQLite database (auto-generated)
├── tests/
│   ├── __init__.py
│   ├── test_models.py             # Schema validation tests
│   ├── test_database.py           # SQLite database unit & server integration tests
│   ├── test_parser.py             # Parsing & categorization tests
│   ├── test_agent.py              # End-to-end pipeline & reporting tests
│   ├── test_dashboard.py          # HTML dashboard structure & export tests
│   ├── test_server.py             # FastAPI REST endpoints & filtering tests
│   └── test_mcp.py                # MCP server protocol & tool tests
└── main.py                        # CLI entry point with optional --web server flag
```

---

## 🏆 Hackathon Submission Details & Checklist

- **Event**: CALL-E Hackathon ("Your Code Is Calling" 2026)
- **Target Track**: Real-World Enterprise Voice Agents / Supply Chain Automation
- **Contribution Areas**: 
  - `Agent Skills` ([`skills/supply-chain-agent/SKILL.md`](skills/supply-chain-agent/SKILL.md))
  - `Workflow Plugins / Functional Applications` ([`src/mcp_server.py`](src/mcp_server.py) & [`main.py`](main.py))
- **Community Submission**: Pull Request to [`CALLE-AI/awesome-phone-call-agents`](https://github.com/CALLE-AI/awesome-phone-call-agents) ([PR #440](https://github.com/CALLE-AI/awesome-phone-call-agents/pull/440))
- **Additional CALL-E Credits Blurb**: [`docs/CALL_E_CREDITS_BLURB.md`](docs/CALL_E_CREDITS_BLURB.md)
- **Devpost Submission Requirements**:
  - Pull Request URL on `CALLE-AI/awesome-phone-call-agents`
  - 3-minute public demonstration video on YouTube or Vimeo
  - Email address associated with CALL-E account
  - Link to open-source repository ([`mohSadiq90/call-e-hackathon`](https://github.com/mohSadiq90/call-e-hackathon))
  - CALL-E Feedback Survey submission
- **Author**: Mohammad Sadiq ([@mohSadiq90](https://github.com/mohSadiq90))
- **Detailed Guide**: See [INSTRUCTIONS.md](INSTRUCTIONS.md) for step-by-step instructions.

