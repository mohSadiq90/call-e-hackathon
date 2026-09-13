---
name: calle-supply-chain-agent
description: Outbound phone agent powered by CALL-E that calls suppliers to check fulfillment status on purchase orders, negotiates revised dates, captures delay root causes, and generates structured procurement intelligence.
version: 1.0.0
author: mohSadiq90
tags:
  - phone-call-agent
  - telephony
  - supply-chain
  - call-e
  - procurement
---

# 📞 CALL-E Supply Chain Supplier Status Check Agent Skill

## Overview
This skill equips an AI agent with the ability to initiate autonomous outbound telephone calls to supply chain vendors and suppliers using the **CALL-E SDK / API**. 

The agent conducts structured 5-step fulfillment conversations:
1. Greets the dispatcher and states identity / recorded line compliance.
2. Checks binary fulfillment status against committed PO deadline.
3. Categorizes delay root causes (`RAW_MATERIAL_SHORTAGE`, `LOGISTICS_PORT_CONGESTION`, `QUALITY_CONTROL_HOLD`, `EQUIPMENT_FAILURE`, `LABOR_SHORTAGE`).
4. Negotiates revised delivery commitments, expedited shipping, or partial delivery.
5. Quantifies financial penalty risk and records supervisor escalation details.

---

## When to Use This Skill
Activate this skill when:
- An enterprise user asks to verify upcoming purchase orders or vendor delivery dates.
- An ERP system detects purchase orders nearing delivery milestones with high stockout risk.
- You need to trigger outbound telephony calls to suppliers and extract structured JSON/CSV reports.

---

## Tools & Commands

### 1. Batch Execution
```bash
python3 main.py --data data/suppliers.json --output-dir output/
```

### 2. Single Supplier Check
```bash
python3 main.py --supplier SUP-102
```

### 3. Live CALL-E Telephony (Outbound Call)
```bash
python3 main.py --live --supplier SUP-101 --company-name "Enterprise Procurement"
```

### 4. High-Fidelity Simulation Mode (Zero-Credit)
```bash
python3 main.py --mock
```

---

## Output Data Schemas

### Call Result JSON
```json
{
  "call_id": "call_mock_SUP-102_1789034",
  "supplier_id": "SUP-102",
  "purchase_order_id": "PO-88120",
  "fulfillment_status": "DELAYED",
  "revised_delivery_date": "2026-09-20",
  "delay_days": 5,
  "delay_reason_category": "RAW_MATERIAL_SHORTAGE",
  "delay_reason_details": "Polymer resin adhesive shipment delayed at port.",
  "estimated_financial_exposure_usd": 8350.0,
  "escalation_contact_name": "Maria Gomez",
  "escalation_contact_phone": "+1-555-***-9923",
  "requires_escalation": true
}
```

### Procurement CSV Report
Columns:
`call_id,supplier_id,supplier_name,po_id,original_date,revised_date,delay_days,status,category,financial_exposure_usd,escalation_lead,phone`

---

## Safety, Authorization & Cancellation Boundaries
1. **Explicit Operator Authorization:** Requires explicit per-run operator intent (`authorization_confirmed: true`) and destination authorization (`destination_authorized: true`) before initiating calls.
2. **Ambiguity Stop Contract:** Fails closed to a human operator when PO, vendor, or contact phone parameters are ambiguous or unverified.
3. **Redaction & Privacy Masking:** All user-facing telephone numbers and provider-specific telemetry are masked (e.g. `+1-555-***-9923`).
4. **Cancellation Limits:** The CALL-E Calls API does not support in-flight call cancellation once dispatched to the carrier network. Closing the UI or process does not recall active calls; keep verification waves small.
