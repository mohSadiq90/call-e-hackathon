#!/usr/bin/env python3
"""
Generates high-fidelity curated enterprise dataset of 14 supplier verification calls.
Contains exactly 2 records for each delay root cause category (NONE/On-time,
Raw Material Shortage, Quality Control Hold, Production Halt, Logistics Port Congestion,
Weather Force Majeure, and Other/Unreachable), providing a clean, balanced demo experience.
"""

import json
import csv
from pathlib import Path

ENTERPRISE_SUPPLIERS = [
    # 1. On-Time (NONE) - #1
    {
        "supplier": {
            "id": "SUP-101",
            "name": "Apex Microelectronics Corp",
            "contact_name": "David Miller",
            "phone": "+1-555-010-4821",
            "email": "dmiller@apexmicro.com",
            "category": "Critical Electronics",
            "timezone": "America/Chicago"
        },
        "order": {
            "order_id": "PO-91001",
            "supplier_id": "SUP-101",
            "item_description": "Optical Proximity Sensors (Model OP-40)",
            "quantity": 10000,
            "unit_cost_usd": 4.50,
            "total_value_usd": 45000.00,
            "committed_delivery_date": "2026-09-18",
            "destination_facility": "DC-04 Bentonville Facility"
        },
        "mock_scenario": {
            "status": "ON_TIME",
            "revised_date": "2026-09-18",
            "delay_days": 0,
            "delay_category": "NONE",
            "reason": "All 10,000 sensors passed QA testing and departed our Austin plant via FedEx Freight.",
            "expedited_freight_cost": 0.0,
            "escalation_name": "David Miller",
            "escalation_phone": "+1-555-010-4821"
        }
    },
    # 2. On-Time (NONE) - #2
    {
        "supplier": {
            "id": "SUP-104",
            "name": "Metro Fasteners & Industrial Hardware",
            "contact_name": "Samira Khan",
            "phone": "+1-555-019-3312",
            "email": "skhan@metrofasteners.com",
            "category": "Standard Hardware",
            "timezone": "America/Chicago"
        },
        "order": {
            "order_id": "PO-91004",
            "supplier_id": "SUP-104",
            "item_description": "M6 Grade 8 Stainless Steel Flange Bolts",
            "quantity": 50000,
            "unit_cost_usd": 0.15,
            "total_value_usd": 7500.00,
            "committed_delivery_date": "2026-09-14",
            "destination_facility": "DC-12 Atlanta Distribution Hub"
        },
        "mock_scenario": {
            "status": "ON_TIME",
            "revised_date": "2026-09-14",
            "delay_days": 0,
            "delay_category": "NONE",
            "reason": "Palletized and staged on loading dock, scheduled for pickup by Old Dominion Freight.",
            "expedited_freight_cost": 0.0,
            "escalation_name": "Samira Khan",
            "escalation_phone": "+1-555-019-3312"
        }
    },
    # 3. Raw Material Shortage - #1 (Verified Real Call Reference)
    {
        "supplier": {
            "id": "SUP-REAL-001",
            "name": "MicroSilicon Global Corp",
            "contact_name": "Dave / Fulfillment Coordinator",
            "phone": "+1-563-281-3105",
            "email": "dave@microsiliconglobal.com",
            "category": "Critical Electronics",
            "timezone": "America/Chicago"
        },
        "order": {
            "order_id": "PO-88219",
            "supplier_id": "SUP-REAL-001",
            "item_description": "5,000 Microcontroller Units",
            "quantity": 5000,
            "unit_cost_usd": 28.50,
            "total_value_usd": 142500.00,
            "committed_delivery_date": "2026-09-15",
            "destination_facility": "DC-04 Bentonville Facility"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-22",
            "delay_days": 7,
            "delay_category": "RAW_MATERIAL_SHORTAGE",
            "reason": "Wafer fabrication substrate delay and raw silicon batch backorder.",
            "expedited_freight_cost": 3200.0,
            "escalation_name": "Dave / Fulfillment Coordinator",
            "escalation_phone": "+1-563-281-3105"
        }
    },
    # 4. Raw Material Shortage - #2 (Partial Dispatch)
    {
        "supplier": {
            "id": "SUP-102",
            "name": "Pacific Packaging Solutions",
            "contact_name": "Maria Gomez",
            "phone": "+1-555-014-9923",
            "email": "mgomez@pacificpackaging.com",
            "category": "Packaging & Corrugated",
            "timezone": "America/Los_Angeles"
        },
        "order": {
            "order_id": "PO-91002",
            "supplier_id": "SUP-102",
            "item_description": "Heavy-Duty Corrugated Master Cartons (24x18x18)",
            "quantity": 25000,
            "unit_cost_usd": 1.20,
            "total_value_usd": 30000.00,
            "committed_delivery_date": "2026-09-15",
            "destination_facility": "DC-08 Dallas Logistics Center"
        },
        "mock_scenario": {
            "status": "PARTIAL_DISPATCH",
            "revised_date": "2026-09-20",
            "delay_days": 5,
            "delay_category": "RAW_MATERIAL_SHORTAGE",
            "reason": "Polymer resin adhesive shipment delayed at the port; 15,000 cartons shipped today, remaining 10,000 delayed.",
            "expedited_freight_cost": 850.0,
            "escalation_name": "Maria Gomez (Operations Manager)",
            "escalation_phone": "+1-555-014-9923"
        }
    },
    # 5. Quality Control Hold - #1
    {
        "supplier": {
            "id": "SUP-103",
            "name": "Global Precision Machining",
            "contact_name": "Arthur Pendelton",
            "phone": "+1-555-018-7734",
            "email": "apendelton@globalprecision.com",
            "category": "Castings & Enclosures",
            "timezone": "America/Detroit"
        },
        "order": {
            "order_id": "PO-91003",
            "supplier_id": "SUP-103",
            "item_description": "Die-Cast Aluminum Sensor Enclosures",
            "quantity": 3000,
            "unit_cost_usd": 18.50,
            "total_value_usd": 55500.00,
            "committed_delivery_date": "2026-09-16",
            "destination_facility": "DC-04 Bentonville Facility"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-22",
            "delay_days": 6,
            "delay_category": "QUALITY_CONTROL_HOLD",
            "reason": "Batch calibration variance detected during coordinate measuring inspection; re-machining required.",
            "expedited_freight_cost": 2200.0,
            "escalation_name": "Karen Vance (VP Quality)",
            "escalation_phone": "+1-555-018-7740"
        }
    },
    # 6. Quality Control Hold - #2 (Partial Dispatch)
    {
        "supplier": {
            "id": "SUP-125",
            "name": "NexGen Circuitry Labs",
            "contact_name": "Julian Zhao",
            "phone": "+1-555-085-7766",
            "email": "jzhao@nexgencircuit.com",
            "category": "Critical Electronics",
            "timezone": "America/Los_Angeles"
        },
        "order": {
            "order_id": "PO-91025",
            "supplier_id": "SUP-125",
            "item_description": "12-Layer HDI Printed Circuit Board Assemblies",
            "quantity": 4500,
            "unit_cost_usd": 38.00,
            "total_value_usd": 171000.00,
            "committed_delivery_date": "2026-09-20",
            "destination_facility": "DC-06 Chicago Tech Hub"
        },
        "mock_scenario": {
            "status": "PARTIAL_DISPATCH",
            "revised_date": "2026-09-24",
            "delay_days": 4,
            "delay_category": "QUALITY_CONTROL_HOLD",
            "reason": "First batch of 3,000 PCBs passed automated optical inspection and shipped; 1,500 units held for solder-mask re-cure.",
            "expedited_freight_cost": 1800.0,
            "escalation_name": "Julian Zhao (Engineering Director)",
            "escalation_phone": "+1-555-085-7766"
        }
    },
    # 7. Production Halt - #1
    {
        "supplier": {
            "id": "SUP-107",
            "name": "Titan Heavy Dynamics",
            "contact_name": "Marcus Thorne",
            "phone": "+1-555-023-4112",
            "email": "mthorne@titanheavy.com",
            "category": "Heavy Mechanics",
            "timezone": "America/Chicago"
        },
        "order": {
            "order_id": "PO-91007",
            "supplier_id": "SUP-107",
            "item_description": "Structural Steel Chassis Crossmembers",
            "quantity": 800,
            "unit_cost_usd": 95.00,
            "total_value_usd": 76000.00,
            "committed_delivery_date": "2026-09-21",
            "destination_facility": "DC-08 Dallas Logistics Center"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-28",
            "delay_days": 7,
            "delay_category": "PRODUCTION_HALT",
            "reason": "Robotic welding cell spindle bearing failure halted assembly line 3 for 72 hours.",
            "expedited_freight_cost": 2800.0,
            "escalation_name": "Marcus Thorne (Plant Manager)",
            "escalation_phone": "+1-555-023-4112"
        }
    },
    # 8. Production Halt - #2
    {
        "supplier": {
            "id": "SUP-122",
            "name": "Mach Precision Castings",
            "contact_name": "Evelyn Reed",
            "phone": "+1-555-074-6688",
            "email": "ereed@machprecision.com",
            "category": "Castings & Enclosures",
            "timezone": "America/Detroit"
        },
        "order": {
            "order_id": "PO-91022",
            "supplier_id": "SUP-122",
            "item_description": "Sand-Cast Magnesium Motor Housings",
            "quantity": 1200,
            "unit_cost_usd": 52.00,
            "total_value_usd": 62400.00,
            "committed_delivery_date": "2026-09-19",
            "destination_facility": "DC-08 Dallas Logistics Center"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-26",
            "delay_days": 7,
            "delay_category": "PRODUCTION_HALT",
            "reason": "Induction melting furnace crucible lining inspection showed degradation, requiring emergency refit.",
            "expedited_freight_cost": 3500.0,
            "escalation_name": "Evelyn Reed (VP Manufacturing)",
            "escalation_phone": "+1-555-074-6688"
        }
    },
    # 9. Logistics Port Congestion - #1
    {
        "supplier": {
            "id": "SUP-105",
            "name": "Zenith Hydraulics & Motion Systems",
            "contact_name": "Robert Hayes",
            "phone": "+1-555-012-6644",
            "email": "rhayes@zenithmotion.com",
            "category": "Electro-Mechanical",
            "timezone": "America/New_York"
        },
        "order": {
            "order_id": "PO-91005",
            "supplier_id": "SUP-105",
            "item_description": "Double-Acting Hydraulic Actuator Cylinders",
            "quantity": 400,
            "unit_cost_usd": 125.00,
            "total_value_usd": 50000.00,
            "committed_delivery_date": "2026-09-17",
            "destination_facility": "DC-04 Bentonville Facility"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-24",
            "delay_days": 7,
            "delay_category": "LOGISTICS_PORT_CONGESTION",
            "reason": "Intermodal rail container hold at Port of Long Beach caused a 5-day inland transit delay.",
            "expedited_freight_cost": 3400.0,
            "escalation_name": "Robert Hayes (Operations Director)",
            "escalation_phone": "+1-555-012-6644"
        }
    },
    # 10. Logistics Port Congestion - #2
    {
        "supplier": {
            "id": "SUP-131",
            "name": "OptoCore Photonics Corp",
            "contact_name": "Valerie Chang",
            "phone": "+1-555-104-3311",
            "email": "vchang@optocore.com",
            "category": "Optics & Sensors",
            "timezone": "America/Los_Angeles"
        },
        "order": {
            "order_id": "PO-91031",
            "supplier_id": "SUP-131",
            "item_description": "Fiber Optic Transceiver Modules (100G QSFP28)",
            "quantity": 800,
            "unit_cost_usd": 135.00,
            "total_value_usd": 108000.00,
            "committed_delivery_date": "2026-09-21",
            "destination_facility": "DC-06 Chicago Tech Hub"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-27",
            "delay_days": 6,
            "delay_category": "LOGISTICS_PORT_CONGESTION",
            "reason": "Laser diode component air shipment stranded during Singapore transit hub customs audit.",
            "expedited_freight_cost": 2700.0,
            "escalation_name": "Valerie Chang (Global Supply Director)",
            "escalation_phone": "+1-555-104-3311"
        }
    },
    # 11. Weather / Force Majeure - #1
    {
        "supplier": {
            "id": "SUP-114",
            "name": "Cascade Thermal Solutions",
            "contact_name": "Chloe Bennett",
            "phone": "+1-555-049-5520",
            "email": "cbennett@cascadethermal.com",
            "category": "Electro-Mechanical",
            "timezone": "America/Los_Angeles"
        },
        "order": {
            "order_id": "PO-91014",
            "supplier_id": "SUP-114",
            "item_description": "Extruded Aluminum Heat Sink Arrays",
            "quantity": 8000,
            "unit_cost_usd": 6.80,
            "total_value_usd": 54400.00,
            "committed_delivery_date": "2026-09-17",
            "destination_facility": "DC-06 Chicago Tech Hub"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-23",
            "delay_days": 6,
            "delay_category": "WEATHER_FORCE_MAJEURE",
            "reason": "Severe tropical storm flood advisory forced 3-day closure of Louisiana anodizing plant.",
            "expedited_freight_cost": 1900.0,
            "escalation_name": "Chloe Bennett (Regional Operations Lead)",
            "escalation_phone": "+1-555-049-5520"
        }
    },
    # 12. Weather / Force Majeure - #2
    {
        "supplier": {
            "id": "SUP-153",
            "name": "Gulf Coast Chemical Logistics",
            "contact_name": "Darren Miller",
            "phone": "+1-555-175-8833",
            "email": "dmiller@gulfcoastchem.com",
            "category": "Raw Materials & Chemicals",
            "timezone": "America/Chicago"
        },
        "order": {
            "order_id": "PO-91053",
            "supplier_id": "SUP-153",
            "item_description": "Industrial Solvent & Resin Clarifiers (55-Gal Drums)",
            "quantity": 200,
            "unit_cost_usd": 240.00,
            "total_value_usd": 48000.00,
            "committed_delivery_date": "2026-09-18",
            "destination_facility": "DC-08 Dallas Logistics Center"
        },
        "mock_scenario": {
            "status": "DELAYED",
            "revised_date": "2026-09-25",
            "delay_days": 7,
            "delay_category": "WEATHER_FORCE_MAJEURE",
            "reason": "Gulf Coast hurricane track shut down port terminals and flooded interstate rail spurs.",
            "expedited_freight_cost": 2400.0,
            "escalation_name": "Darren Miller (Logistics Supervisor)",
            "escalation_phone": "+1-555-175-8833"
        }
    },
    # 13. Other / Unreachable - #1
    {
        "supplier": {
            "id": "SUP-115",
            "name": "Summit Precision Seals",
            "contact_name": "Frank Donato",
            "phone": "+1-555-052-7711",
            "email": "fdonato@summitseals.com",
            "category": "Standard Hardware",
            "timezone": "America/New_York"
        },
        "order": {
            "order_id": "PO-91015",
            "supplier_id": "SUP-115",
            "item_description": "Viton High-Temperature O-Ring Gaskets",
            "quantity": 40000,
            "unit_cost_usd": 0.45,
            "total_value_usd": 18000.00,
            "committed_delivery_date": "2026-09-16",
            "destination_facility": "DC-04 Bentonville Facility"
        },
        "mock_scenario": {
            "status": "UNREACHABLE",
            "revised_date": None,
            "delay_days": 0,
            "delay_category": "OTHER",
            "reason": "Automated switchboard loop with no dispatcher response; voicemail inbox full.",
            "expedited_freight_cost": 0.0,
            "escalation_name": "Frank Donato",
            "escalation_phone": "+1-555-052-7711"
        }
    },
    # 14. Other / Unreachable - #2
    {
        "supplier": {
            "id": "SUP-138",
            "name": "Cascade Paperboard Systems",
            "contact_name": "Timothy Vance",
            "phone": "+1-555-129-1122",
            "email": "tvance@cascadepaper.com",
            "category": "Packaging & Corrugated",
            "timezone": "America/Chicago"
        },
        "order": {
            "order_id": "PO-91038",
            "supplier_id": "SUP-138",
            "item_description": "Recycled Kraft Linerboard Rolls (50-lb Basis)",
            "quantity": 500,
            "unit_cost_usd": 82.00,
            "total_value_usd": 41000.00,
            "committed_delivery_date": "2026-09-16",
            "destination_facility": "DC-12 Atlanta Distribution Hub"
        },
        "mock_scenario": {
            "status": "UNREACHABLE",
            "revised_date": None,
            "delay_days": 0,
            "delay_category": "OTHER",
            "reason": "Out of service recording encountered; dispatch line unmonitored.",
            "expedited_freight_cost": 0.0,
            "escalation_name": "Timothy Vance",
            "escalation_phone": "+1-555-129-1122"
        }
    }
]


def generate_enterprise_data(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "suppliers_enterprise_50.json"
    csv_path = output_dir / "suppliers_enterprise_50.csv"

    # Write JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ENTERPRISE_SUPPLIERS, f, indent=2)
    print(f"Generated {len(ENTERPRISE_SUPPLIERS)} curated supplier POs to {json_path}")

    # Write CSV
    rows = []
    for item in ENTERPRISE_SUPPLIERS:
        s = item["supplier"]
        o = item["order"]
        m = item["mock_scenario"]
        rows.append({
            "supplier_id": s["id"],
            "supplier_name": s["name"],
            "contact_name": s["contact_name"],
            "phone": s["phone"],
            "email": s["email"],
            "category": s["category"],
            "timezone": s["timezone"],
            "order_id": o["order_id"],
            "item_description": o["item_description"],
            "quantity": o["quantity"],
            "unit_cost_usd": o["unit_cost_usd"],
            "total_value_usd": o["total_value_usd"],
            "committed_delivery_date": o["committed_delivery_date"],
            "destination_facility": o["destination_facility"],
            "scenario_status": m["status"],
            "scenario_revised_date": m["revised_date"] or "",
            "scenario_delay_days": m["delay_days"],
            "scenario_delay_category": m["delay_category"],
            "scenario_reason": m["reason"],
            "scenario_expedited_freight_cost": m["expedited_freight_cost"],
            "scenario_escalation_name": m["escalation_name"],
            "scenario_escalation_phone": m["escalation_phone"],
        })

    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Generated CSV export to {csv_path}")


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "data"
    generate_enterprise_data(data_dir)
