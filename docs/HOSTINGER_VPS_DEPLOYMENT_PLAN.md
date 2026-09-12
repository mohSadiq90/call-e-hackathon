# Hostinger VPS Deployment & Web Workflow Plan 🌐

**Domain Target:** `calle.fyro.cloud` (or `supplychain.fyro.cloud`)  
**Project:** CALL-E Autonomous Supply Chain Telephony Platform  
**Target Host:** Hostinger VPS (Ubuntu / Debian Linux)  
**Status:** Architecture Designed & Deployment Scripts Prepared (Pending User Approval)

---

## 1. Executive Summary: Feasibility & Vision

### Can we host the CALL-E project on our Hostinger VPS with a subdomain of `fyro.cloud`?
**Yes, absolutely.** The CALL-E platform has been architected as a lightweight, production-grade Python 3.12 application powered by **FastAPI**, **Uvicorn**, and **Pydantic**, serving a self-contained, reactive **Executive Operations Dashboard** (`output/procurement_dashboard.html`).

Hosting this on a Hostinger VPS gives our project:
1. **A Public Live URL for Hackathon Judges & Devpost**: e.g., `https://calle.fyro.cloud`.
2. **An Interactive Workflow Trigger Center**: A single portal where anyone can trigger live outbound phone calls or zero-credit simulations, test batch runs across 52 enterprise suppliers, and inspect real-time results.
3. **An Operations Dashboard**: Live KPIs, delay root cause analytics, financial exposure calculations ($437k+ risk tracked), and audio call playback.
4. **Public REST API & Swagger UI**: Live `/docs` endpoint for developers, ERP integrations, or MCP agents.

---

## 2. Core Enterprise Use Case & Value Proposition

### 🏢 The Business Problem
In enterprise supply chains (e.g. Walmart, Boeing, Target), procurement and fulfillment teams lose **2 to 3 hours per manager every single day** manually dialing dozens of vendors to confirm if purchase orders will arrive by deadline. When delays are uncovered too late:
- Assembly lines and retail shelves sit empty.
- Emergency air freight surcharges skyrocket ($10,000+ per shipment).
- SLA delay penalties accumulate exponentially.

### 🤖 The CALL-E Web Solution
The web application at `https://calle.fyro.cloud` acts as an **Autonomous Supply Chain Mission Control Center**:
- **Proactive Voice AI Dialing**: Connects with supplier dispatchers across timezones to verify order fulfillment.
- **Deterministic 5-Step Conversational Protocol**: Confirms deadlines, diagnoses delay root causes (`RAW_MATERIAL_SHORTAGE`, `LOGISTICS_PORT_CONGESTION`, `QUALITY_CONTROL_HOLD`), negotiates recovery dates, and calculates financial risk.
- **Dual Telephony Modality**:
  - **Live CALL-E PSTN Network**: Physically dials live phone numbers for real demonstrations.
  - **High-Fidelity AI Simulator**: Instant realistic simulations with zero API credit burn for hackathon reviewers and high-volume testing.
- **Automated ERP Sync**: Exports verified status updates directly to SAP, Oracle, and CSV spreadsheets.

---

## 3. End-to-End User Flow on the Hosted Webpage

```
+---------------------------------------------------------------------------------------+
|                               https://calle.fyro.cloud                                |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
   +---------------------------------------------------------------------------------+
   | [Step 1: Executive Control Tower]                                              |
   | - 6 Global KPIs: Total Orders (52), On-Time Rate (67%), Financial Risk ($437k)  |
   | - Visual Analytics: Root Cause Delay Breakdown, Status Distribution Bars        |
   +---------------------------------------------------------------------------------+
                                           |
                                           v
   +---------------------------------------------------------------------------------+
   | [Step 2: Workflow Trigger Center]                                              |
   | - Single Call Trigger: Dial user's phone or test supplier                      |
   | - Batch Runner: Trigger verification batch across 52 suppliers or category     |
   | - Preset Scenarios: One-click simulation of Port Congestion, Material Shortage   |
   +---------------------------------------------------------------------------------+
                                           |
                                           v
   +---------------------------------------------------------------------------------+
   | [Step 3: Autonomous Telephony Execution]                                       |
   | - Live Mode: CALL-E dials PSTN phone line & speaks to dispatcher                |
   | - Simulated Mode: High-fidelity engine executes 5-step conversational protocol |
   +---------------------------------------------------------------------------------+
                                           |
                                           v
   +---------------------------------------------------------------------------------+
   | [Step 4: Real-Time Intelligence & Dashboard Ingestion]                         |
   | - Extracted Pydantic record prepended to top of active audit log               |
   | - Dynamic KPIs recalculate instantly (Financial risk, On-time %, Escalations)   |
   +---------------------------------------------------------------------------------+
                                           |
                                           v
   +---------------------------------------------------------------------------------+
   | [Step 5: Inspection, Audio Waveform & Action]                                  |
   | - Click call row -> Opens detailed modal with conversational transcript bubbles|
   | - Play audio call recording with animated waveform & speed controls (1x, 2x)   |
   | - View Emergency Escalation Contact & download 1-click ERP CSV/JSON export      |
   +---------------------------------------------------------------------------------+
```

### Detailed Webpage Actions:
1. **Trigger Single Supplier Verification**:
   - User clicks **"+ Trigger Verification Call"** in the top navigation bar.
   - Form opens with fields pre-populated or customizable: Supplier Name, PO ID, Item Description, Delivery Date, and Target Phone Number.
   - Mode Toggle: **Live CALL-E Telephony** (real call) vs **Offline Simulator** (instant demo).
   - Upon dispatch, the call is executed, parsed, and injected into the dashboard table in real time.
2. **Trigger Batch Procurement Verification**:
   - Single-click batch execution across supplier categories (e.g. Critical Electronics, Packaging, Heavy Mechanics).
   - Verifies 5 to 50 suppliers sequentially and updates the entire control tower.
3. **Interactive Search & Multi-Pill Filtering**:
   - Filter instantly by status (`ON_TIME`, `DELAYED`, `PARTIAL_DISPATCH`, `UNREACHABLE`, `ESCALATIONS`).
   - Full-text search across PO numbers, vendor names, line items, and contacts.
4. **Call Inspection & Audio Player Modal**:
   - Complete conversational transcript between AI agent and supplier dispatcher.
   - Equalizer waveform audio player with 1.0x, 1.5x, and 2.0x playback speeds.
   - Manager escalation card with click-to-call and click-to-email.
5. **One-Click ERP Export**:
   - Download freshly compiled `procurement_status_report.csv` and `procurement_status_report.json`.

---

## 4. Technical Architecture on Hostinger VPS

```
                          [ Inbound Internet Traffic ]
                                       |
                                       v
                     [ DNS: calle.fyro.cloud (A Record) ]
                                       |
                                       v
                    +-------------------------------------+
                    |       Hostinger Linux VPS           |
                    |                                     |
                    |  +-------------------------------+  |
                    |  |       Nginx (Port 80/443)     |  |
                    |  |   - Let's Encrypt SSL (HTTPS) |  |
                    |  |   - WebSocket / SSE Support   |  |
                    |  |   - Reverse Proxy to :8000    |  |
                    |  +---------------+---------------+  |
                    |                  |                  |
                    |                  v                  |
                    |  +-------------------------------+  |
                    |  |  FastAPI / Uvicorn (:8000)    |  |
                    |  |   - Systemd: calle.service    |  |
                    |  |   - REST API & Webhooks       |  |
                    |  |   - Dynamic HTML Dashboard    |  |
                    |  |   - CALL-E SDK Client         |  |
                    |  |   - Simulation Engine         |  |
                    |  +-------------------------------+  |
                    +-------------------------------------+
```

### Infrastructure Specifications:
- **Web Server:** Uvicorn running FastAPI on `127.0.0.1:8000` (managed via Systemd `calle.service` or Docker).
- **Reverse Proxy:** Nginx with HTTP/2, Let's Encrypt SSL, Gzip compression, and security headers.
- **SSL Certificate:** Automated Zero-Cost SSL via Certbot (`certbot --nginx -d calle.fyro.cloud`).
- **Resource Footprint:** Very lightweight (< 150MB RAM, < 0.5% CPU idle), well within any Hostinger VPS tier (KVM 1 / KVM 2).

---

## 5. DNS Setup Guide for `fyro.cloud`

To connect the subdomain, add a single DNS `A` record in Hostinger:

1. Log into your **Hostinger Control Panel (hPanel)**.
2. Navigate to **Domains** -> **fyro.cloud** -> **DNS / Nameservers**.
3. Add the following record:
   - **Type:** `A`
   - **Name:** `calle` (this creates `calle.fyro.cloud`)
   - **Points to:** `<YOUR_HOSTINGER_VPS_IP_ADDRESS>`
   - **TTL:** `300` (5 minutes)
4. Save the record. DNS propagation typically takes 1 to 5 minutes.

*(Alternative subdomain options if preferred: `call-e.fyro.cloud`, `supplychain.fyro.cloud`, `procurement.fyro.cloud`)*.

---

## 6. Deployment Assets Prepared in Repository

All deployment configuration files have been prepared and tested in `/home/appdemo885/call-e-hackathon/deploy/`:

| File | Purpose |
|---|---|
| [`deploy/nginx/calle.fyro.cloud.conf`](file:///home/appdemo885/call-e-hackathon/deploy/nginx/calle.fyro.cloud.conf) | Nginx reverse proxy, HTTPS/SSL, WebSockets, and security headers. |
| [`deploy/calle.service`](file:///home/appdemo885/call-e-hackathon/deploy/calle.service) | Systemd unit file ensuring the backend automatically starts on VPS reboot. |
| [`deploy/Dockerfile`](file:///home/appdemo885/call-e-hackathon/deploy/Dockerfile) | Multi-stage Docker container build for containerized deployments. |
| [`deploy/docker-compose.yml`](file:///home/appdemo885/call-e-hackathon/deploy/docker-compose.yml) | Docker Compose orchestration file. |
| [`deploy/.env.production.example`](file:///home/appdemo885/call-e-hackathon/deploy/.env.production.example) | Template for VPS environment variables and API keys. |
| [`deploy/deploy_hostinger.sh`](file:///home/appdemo885/call-e-hackathon/deploy/deploy_hostinger.sh) | 1-command automated deployment script for the VPS. |

---

## 7. How Deployment Will Be Executed (Upon User Approval)

Once you approve, deployment on the Hostinger VPS can be completed in under 2 minutes:

### Option 1: 1-Command Automated Script (Recommended)
SSH into your Hostinger VPS and run:
```bash
curl -sSL https://raw.githubusercontent.com/mohSadiq90/call-e-hackathon/main/deploy/deploy_hostinger.sh | bash
```
*Or clone and execute:*
```bash
git clone https://github.com/mohSadiq90/call-e-hackathon.git /var/www/call-e-hackathon
cd /var/www/call-e-hackathon
./deploy/deploy_hostinger.sh
```

### Option 2: Docker Compose (Alternative)
```bash
cd /var/www/call-e-hackathon/deploy
docker compose up -d --build
```

---

## 8. Questions for User Approval Before Proceeding

To proceed with the live VPS implementation, please confirm:
1. **Subdomain Preference:** Is `calle.fyro.cloud` your preferred subdomain, or would you prefer `supplychain.fyro.cloud` / `procure.fyro.cloud`?
2. **VPS Credentials / Access:** Would you like us to provide the exact 1-liner command for you to run on your Hostinger terminal, or do you have SSH connection details for us to deploy directly?
3. **CALL-E Live Telephony vs Demo Safeguards:** On the public page, should live phone calls be open or should live calls require an admin token/key while the high-fidelity simulator remains open to everyone?
