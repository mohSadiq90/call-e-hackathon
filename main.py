"""
Main CLI Entry Point for CALL-E Supply Chain Supplier Status Check Agent.
Executes automated phone verification calls, extracts structured fulfillment data,
and generates procurement intelligence reports.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

from config.settings import DATA_DIR, OUTPUT_DIR
from src.models import Supplier, PurchaseOrder, CallResult
from src.calle_client import CalleSupplierAgentClient
from src.reporter import ProcurementReporter
from src.database import ProcurementDatabase


def load_suppliers(json_path: Path) -> List[Dict[str, Any]]:
    """Loads supplier and purchase order records from JSON."""
    if not json_path.exists():
        print(f"[ERROR] Supplier data file not found: {json_path}")
        sys.exit(1)
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="CALL-E Autonomous Phone Agent for Supply Chain Supplier Status Verification."
    )
    parser.add_argument(
        "--data",
        type=str,
        default=str(DATA_DIR / "suppliers.json"),
        help="Path to supplier input JSON dataset",
    )
    parser.add_argument(
        "--supplier",
        type=str,
        default=None,
        help="Run verification only for a specific Supplier ID (e.g. SUP-101)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        default=True,
        help="Run with live CALL-E phone telephony API (default)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=False,
        help="Run in high-fidelity simulation mode (zero API cost)",
    )
    parser.add_argument(
        "--company-name",
        type=str,
        default="Enterprise Procurement Operations",
        help="Company name used by agent when introducing herself",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(OUTPUT_DIR),
        help="Directory to save CSV, JSON, and HTML reports",
    )
    parser.add_argument(
        "--web",
        "--serve",
        action="store_true",
        help="Launch interactive web dashboard HTTP server after verification",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind web dashboard server (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind web dashboard server (default: 127.0.0.1)",
    )

    args = parser.parse_args()

    use_mock = args.mock

    print("=" * 70)
    print("📞 CALL-E SUPPLY CHAIN AGENT - STARTING STATUS VERIFICATION")
    print(f"• Mode: {'MOCK SIMULATION (Zero API Cost)' if use_mock else 'LIVE TELEPHONY (CALL-E SDK)'}")
    print(f"• Company Identity: {args.company_name}")
    print(f"• Input Dataset: {args.data}")
    print("=" * 70)

    # 1. Load supplier records
    raw_data = load_suppliers(Path(args.data))
    if args.supplier:
        raw_data = [item for item in raw_data if item["supplier"]["id"] == args.supplier]
        if not raw_data:
            print(f"[ERROR] Supplier ID '{args.supplier}' not found in dataset.")
            sys.exit(1)

    print(f"[INFO] Loaded {len(raw_data)} purchase orders scheduled for verification.")

    # 2. Initialize CALL-E Client
    client = CalleSupplierAgentClient(use_mock=use_mock)
    reporter = ProcurementReporter(output_dir=Path(args.output_dir))

    call_results: List[CallResult] = []

    # 3. Execute calls across suppliers
    for idx, item in enumerate(raw_data, start=1):
        supplier = Supplier(**item["supplier"])
        order = PurchaseOrder(**item["order"])
        mock_scenario = item.get("mock_scenario", {})

        print(f"\n[{idx}/{len(raw_data)}] Placing call to {supplier.name} for Order {order.order_id}...")
        result = client.execute_call(
            supplier=supplier,
            order=order,
            company_name=args.company_name,
            scenario_override=mock_scenario,
        )
        call_results.append(result)
        status_symbol = "✅" if result.fulfillment_status.value == "ON_TIME" else "⚠️"
        print(f"    Status: {status_symbol} {result.fulfillment_status.value} | Revised: {result.revised_delivery_date} | Delay: +{result.delay_days}d")

    # 4. Generate Reports & Persist to SQLite
    batch_report = reporter.generate_batch_report(call_results)
    csv_file = reporter.export_csv(call_results)
    json_file = reporter.export_json(batch_report)
    html_file = reporter.export_html(batch_report)

    db = ProcurementDatabase()
    db.save_suppliers_and_orders(raw_data)
    db.upsert_call_results_batch(call_results)

    # 5. Display Console Dashboard
    reporter.print_terminal_dashboard(batch_report)

    print(f"🎉 Verification batch complete!")
    print(f"   • CSV Export      : {csv_file}")
    print(f"   • JSON Export     : {json_file}")
    print(f"   • HTML Dashboard  : {html_file}\n")

    if args.web:
        from src.server import start_server
        print(f"🌐 Launching Interactive Web Dashboard on http://{args.host}:{args.port} ...")
        start_server(host=args.host, port=args.port, dataset_path=Path(args.data))


if __name__ == "__main__":
    main()
