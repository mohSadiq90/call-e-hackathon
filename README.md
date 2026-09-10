# 📞 CALL-E Supply Chain Supplier Status Check Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CALL-E SDK](https://img.shields.io/badge/CALL--E-SDK%20Integrated-success)](https://github.com/CALLE-AI/server-sdk-python)
[![Tests: Passing](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)]()

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

---

## 📊 Live Output & Executive Dashboard

When executed, the agent prints a real-time executive dashboard and outputs clean CSV/JSON ledgers:

```text
================================================================================
  CALL-E AUTONOMOUS PROCUREMENT AGENT - DAILY STATUS REPORT
  Generated: 2026-09-10T10:13:47Z | Report ID: rep_2478d003
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

A comprehensive test suite covers models, transcript parsing, and integration pipelines:

```bash
python3 -m unittest discover -s tests -v
```

Output:
```text
test_mock_call_delayed (test_agent.TestAgentPipeline) ... ok
test_mock_call_on_time (test_agent.TestAgentPipeline) ... ok
test_reporting_export (test_agent.TestAgentPipeline) ... ok
test_call_result_model (test_models.TestModels) ... ok
test_purchase_order_model (test_models.TestModels) ... ok
test_supplier_model (test_models.TestModels) ... ok
test_calculate_delay_days (test_parser.TestTranscriptParser) ... ok
test_parse_cost (test_parser.TestTranscriptParser) ... ok
test_parse_delay_category (test_parser.TestTranscriptParser) ... ok
test_parse_revised_date (test_parser.TestTranscriptParser) ... ok
test_parse_status_delayed (test_parser.TestTranscriptParser) ... ok
test_parse_status_on_time (test_parser.TestTranscriptParser) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.019s

OK
```

---

## 📁 Repository Structure

```
call-e-hackathon/
├── README.md                      # Complete project documentation & pitch
├── PROGRESS.md                    # Project work log and sprint tracker
├── pyproject.toml                 # Package configuration
├── requirements.txt               # Dependencies
├── .env.example                   # Environment configuration template
├── config/
│   ├── __init__.py
│   └── settings.py                # Environment configuration loader
├── prompts/
│   ├── __init__.py
│   ├── supplier_agent_prompt.py   # 5-step conversation flow & system instructions
│   └── system_instructions.md     # Markdown conversation tree reference
├── src/
│   ├── __init__.py
│   ├── models.py                  # Pydantic schemas (PO, Supplier, CallResult)
│   ├── calle_client.py            # CALL-E SDK client + High-fidelity simulator
│   ├── transcript_parser.py       # Deterministic extraction of dates, costs, causes
│   └── reporter.py                # CSV, JSON, and ASCII dashboard generator
├── data/
│   ├── suppliers.json             # 5 realistic test supplier records & scenarios
│   └── suppliers.csv              # CSV format for ERP batch ingestion
├── tests/
│   ├── __init__.py
│   ├── test_models.py             # Schema validation tests
│   ├── test_parser.py             # Parsing & categorization tests
│   └── test_agent.py              # End-to-end pipeline & reporting tests
└── main.py                        # CLI entry point
```

---

## 🏆 Hackathon Submission Details

- **Event**: CALL-E Hackathon ("Your Code Is Calling" 2026)
- **Target Track**: Real-World Enterprise Voice Agents / Supply Chain Automation
- **Community Submission**: Pull Request to [`CALLE-AI/awesome-phone-call-agents`](https://github.com/CALLE-AI/awesome-phone-call-agents)
- **Author**: Mohammad Sadiq ([@mohSadiq90](https://github.com/mohSadiq90))
