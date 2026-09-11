"""
Procurement Dashboard and Aggregation Reporter.
Transforms raw call results into structured CSV, JSON ledgers, and executive console dashboards.
"""

import csv
import json
import uuid
from pathlib import Path
from typing import List
from datetime import datetime

from config.settings import OUTPUT_DIR
from src.models import CallResult, BatchProcurementReport, FulfillmentStatus
from src.html_dashboard import render_html_dashboard


class ProcurementReporter:
    """Aggregates and formats call results for procurement managers and executive dashboards."""

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_batch_report(self, results: List[CallResult]) -> BatchProcurementReport:
        """Computes executive summary statistics and risk metrics across all executed calls."""
        total = len(results)
        on_time = sum(1 for r in results if r.fulfillment_status == FulfillmentStatus.ON_TIME)
        delayed = sum(1 for r in results if r.fulfillment_status == FulfillmentStatus.DELAYED)
        unreachable = sum(1 for r in results if r.fulfillment_status == FulfillmentStatus.UNREACHABLE)
        partial = sum(1 for r in results if r.fulfillment_status == FulfillmentStatus.PARTIAL_DISPATCH)
        pct = (on_time / total * 100.0) if total > 0 else 0.0

        total_financial_risk = sum(r.estimated_financial_impact_usd for r in results)
        critical_escalations = [r for r in results if r.escalation_required]

        return BatchProcurementReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}",
            total_orders_checked=total,
            on_time_count=on_time,
            delayed_count=delayed,
            unreachable_count=unreachable,
            partial_dispatch_count=partial,
            on_time_percentage=round(pct, 1),
            total_financial_risk_usd=round(total_financial_risk, 2),
            critical_escalations=critical_escalations,
            call_records=results,
        )

    def export_csv(self, results: List[CallResult], filename: str = "procurement_status_report.csv") -> Path:
        """Writes call results to a standard CSV file for procurement and ERP ingest."""
        path = self.output_dir / filename
        fieldnames = [
            "call_id",
            "call_status",
            "order_id",
            "supplier_name",
            "contact_name",
            "phone_number",
            "fulfillment_status",
            "original_delivery_date",
            "revised_delivery_date",
            "delay_days",
            "delay_category",
            "delay_notes",
            "expedited_freight_cost_usd",
            "estimated_financial_impact_usd",
            "escalation_contact_name",
            "escalation_contact_phone",
            "escalation_required",
            "call_duration_seconds",
            "timestamp",
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in results:
                row = r.model_dump()
                row.pop("raw_transcript", None)
                writer.writerow(row)

        print(f"[REPORTER] CSV report successfully saved to: {path}")
        return path

    def export_json(self, report: BatchProcurementReport, filename: str = "procurement_status_report.json") -> Path:
        """Writes complete batch report with metadata to a JSON file."""
        path = self.output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, indent=2)

        print(f"[REPORTER] JSON report successfully saved to: {path}")
        return path

    def export_html(self, report: BatchProcurementReport, filename: str = "procurement_dashboard.html", api_base_url: str = "") -> Path:
        """Generates an intuitive, interactive HTML executive dashboard for browser inspection."""
        path = self.output_dir / filename
        html_content = render_html_dashboard(report, api_base_url=api_base_url)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[REPORTER] Interactive HTML Dashboard successfully saved to: {path}")
        return path

    def print_terminal_dashboard(self, report: BatchProcurementReport):
        """Prints a clean ASCII executive dashboard to stdout."""
        border = "=" * 80
        divider = "-" * 80

        print("\n" + border)
        print("  CALL-E AUTONOMOUS PROCUREMENT AGENT - DAILY STATUS REPORT")
        print(f"  Generated: {report.generated_at} | Report ID: {report.report_id}")
        print(border)

        # KPI Summary
        print(f"\n📊 EXECUTIVE KPI SUMMARY:")
        print(f"  • Total Purchase Orders Checked : {report.total_orders_checked}")
        print(f"  • On-Time Fulfillment           : {report.on_time_count} ({report.on_time_percentage}%)")
        print(f"  • Delayed / At-Risk Shipments   : {report.delayed_count}")
        print(f"  • Unreachable Vendors           : {report.unreachable_count}")
        print(f"  • Total Estimated Financial Risk: ${report.total_financial_risk_usd:,.2f}")
        print(f"  • Critical Escalations Required : {len(report.critical_escalations)}")

        # Table Header
        print("\n" + divider)
        header = f"{'ORDER ID':<10} | {'SUPPLIER':<22} | {'STATUS':<9} | {'ORIG DATE':<10} | {'REV DATE':<10} | {'DELAY':<5} | {'RISK ($)':<10}"
        print(header)
        print(divider)

        for r in report.call_records:
            status_icon = "✅ ON_TIME" if r.fulfillment_status == FulfillmentStatus.ON_TIME else "⚠️ DELAYED"
            rev_date = r.revised_delivery_date or "-"
            delay_str = f"+{r.delay_days}d" if r.delay_days > 0 else "0d"
            cost_str = f"${r.estimated_financial_impact_usd:,.0f}" if r.estimated_financial_impact_usd > 0 else "$0"
            supp = (r.supplier_name[:20] + "..") if len(r.supplier_name) > 22 else r.supplier_name
            row_str = f"{r.order_id:<10} | {supp:<22} | {status_icon:<9} | {r.original_delivery_date:<10} | {rev_date:<10} | {delay_str:<5} | {cost_str:<10}"
            print(row_str)

        print(divider)

        # Critical Escalations Alert Section
        if report.critical_escalations:
            print("\n🚨 CRITICAL ESCALATION ACTION REQUIRED:")
            for esc in report.critical_escalations:
                print(f"  • Order {esc.order_id} ({esc.supplier_name}):")
                print(f"    - Delay: {esc.delay_days} days (New Target: {esc.revised_delivery_date})")
                print(f"    - Root Cause: {esc.delay_category.value} ({esc.delay_notes})")
                print(f"    - Expedited Freight: ${esc.expedited_freight_cost_usd:,.2f} | Total Risk: ${esc.estimated_financial_impact_usd:,.2f}")
                print(f"    - Escalation Lead: {esc.escalation_contact_name} ({esc.escalation_contact_phone})")

        print("\n" + border + "\n")
