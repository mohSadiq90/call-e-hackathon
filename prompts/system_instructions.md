# CALL-E Supplier Status Agent - Conversation Flow & Guidelines

## Overview
This document specifies the 5-step conversational agent architecture used by the CALL-E agent to conduct outbound automated phone calls to supply chain vendors.

```
[ Step 1: Greeting & Verification ]
               │
               ▼
[ Step 2: Fulfillment Status Check ]
         │               │
      (On-Time)      (Delayed)
         │               │
         │               ▼
         │       [ Step 3: Root Cause Analysis ]
         │               │
         │               ▼
         │       [ Step 4: Revised Timeline & Mitigation ]
         │               │
         └───────┬───────┘
                 │
                 ▼
[ Step 5: Cost Impact, Escalation & Close ]
                 │
                 ▼
[ Structured JSON Output & Dashboard Sync ]
```

## Step-by-Step Breakdown

### Step 1: Greeting & Verification
- **Purpose**: Authenticate counterparty, state recording disclosure, verify authority.
- **Example**: *"Hello, this is Alex from Enterprise Supply Chain Operations on a recorded line regarding Purchase Order PO-88219. Am I speaking with the order fulfillment manager for Apex Components?"*

### Step 2: Fulfillment & Deadline Check
- **Purpose**: Ask deterministic binary question regarding committed arrival date.
- **Example**: *"I am calling to confirm delivery of PO-88219 for 5,000 Microcontroller Units scheduled for September 15. Is this shipment currently on schedule to arrive by September 15?"*

### Step 3: Delay Root Cause (Conditional)
- **Purpose**: Capture vendor explanation and categorize supply chain disruption.
- **Categories**: Raw Material Shortage, Quality Control Quarantine, Carrier/Customs Delay, Equipment Breakdown.

### Step 4: Revised Timeline & Mitigation
- **Purpose**: Lock in revised delivery date and determine if split shipment or air freight is viable.
- **Example**: *"What is the revised delivery date, and is partial delivery possible?"*

### Step 5: Cost Impact & Escalation
- **Purpose**: Note financial liability / expedited shipping fees, capture supervisor contact, and close.
- **Example**: *"Understood. Please provide the escalation supervisor's direct contact. I have logged the revised arrival of September 22 under ticket ref #PO-88219."*
