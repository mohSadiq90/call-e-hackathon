"""Tests for HTML Dashboard rendering and export in src.html_dashboard."""

import unittest
import tempfile
from pathlib import Path

from src.models import (
    Supplier,
    PurchaseOrder,
    CallResult,
    FulfillmentStatus,
    DelayReasonCategory,
    BatchProcurementReport,
)
from src.html_dashboard import render_html_dashboard
from src.reporter import ProcurementReporter


class TestHtmlDashboard(unittest.TestCase):

    def setUp(self):
        self.sample_result_ontime = CallResult(
            call_id="call_test_001",
            order_id="PO-10001",
            supplier_name="Alpha Tech Solutions",
            contact_name="Alice Smith",
            phone_number="+1-555-111-2222",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.ON_TIME,
            original_delivery_date="2026-09-18",
            revised_delivery_date="2026-09-18",
            delay_days=0,
            delay_category=DelayReasonCategory.NONE,
            delay_notes="Confirmed en route via express carrier.",
            expedited_freight_cost_usd=0.0,
            estimated_financial_impact_usd=0.0,
            escalation_contact_name="Alice Smith",
            escalation_contact_phone="+1-555-111-2222",
            escalation_required=False,
            call_duration_seconds=65,
            raw_transcript="Agent: Is PO-10001 on track?\nSupplier: Yes, arriving Sept 18.",
        )

        self.sample_result_delayed = CallResult(
            call_id="call_test_002",
            order_id="PO-10002",
            supplier_name="Beta Logistics Corp",
            contact_name="Bob Jones",
            phone_number="+1-555-333-4444",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.DELAYED,
            original_delivery_date="2026-09-15",
            revised_delivery_date="2026-09-20",
            delay_days=5,
            delay_category=DelayReasonCategory.RAW_MATERIAL_SHORTAGE,
            delay_notes="Resin shortage delayed assembly line.",
            expedited_freight_cost_usd=850.0,
            estimated_financial_impact_usd=8350.0,
            escalation_contact_name="Bob Jones (Director)",
            escalation_contact_phone="+1-555-333-4444",
            escalation_required=True,
            call_duration_seconds=115,
            raw_transcript="Agent: Is PO-10002 on track?\nSupplier: No, delayed by 5 days due to resin shortage.",
        )

        self.sample_result_partial = CallResult(
            call_id="call_test_003",
            order_id="PO-10003",
            supplier_name="Gamma Wire Harness",
            contact_name="Clara Wu",
            phone_number="+1-555-555-6666",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.PARTIAL_DISPATCH,
            original_delivery_date="2026-09-16",
            revised_delivery_date="2026-09-20",
            delay_days=4,
            delay_category=DelayReasonCategory.QUALITY_CONTROL_HOLD,
            delay_notes="First lot shipped, balance held for QC.",
            expedited_freight_cost_usd=1200.0,
            estimated_financial_impact_usd=7200.0,
            escalation_contact_name="Clara Wu",
            escalation_contact_phone="+1-555-555-6666",
            escalation_required=True,
            call_duration_seconds=95,
            raw_transcript="Agent: Status on PO-10003?\nSupplier: We have a partial dispatch situation.",
        )

        self.sample_result_unreachable = CallResult(
            call_id="call_test_004",
            order_id="PO-10004",
            supplier_name="Delta Seals Inc",
            contact_name="Frank Donato",
            phone_number="+1-555-777-8888",
            call_status="UNREACHABLE",
            fulfillment_status=FulfillmentStatus.UNREACHABLE,
            original_delivery_date="2026-09-16",
            revised_delivery_date="2026-09-16",
            delay_days=0,
            delay_category=DelayReasonCategory.OTHER,
            delay_notes="Voicemail reached, line unmonitored.",
            expedited_freight_cost_usd=0.0,
            estimated_financial_impact_usd=0.0,
            escalation_contact_name="Frank Donato",
            escalation_contact_phone="+1-555-777-8888",
            escalation_required=True,
            call_duration_seconds=28,
            raw_transcript="Agent: Urgent status confirmation needed.\nAutomated: Voicemail recorded.",
        )

        self.report = BatchProcurementReport(
            report_id="rep_test_123",
            total_orders_checked=4,
            on_time_count=1,
            delayed_count=1,
            unreachable_count=1,
            partial_dispatch_count=1,
            on_time_percentage=25.0,
            total_financial_risk_usd=15550.0,
            critical_escalations=[
                self.sample_result_delayed,
                self.sample_result_partial,
                self.sample_result_unreachable,
            ],
            call_records=[
                self.sample_result_ontime,
                self.sample_result_delayed,
                self.sample_result_partial,
                self.sample_result_unreachable,
            ],
        )

    def test_render_html_dashboard_structure(self):
        """Validates that rendered HTML contains all required dashboard sections and metadata."""
        html = render_html_dashboard(self.report)

        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("CALL-E Supply Chain Intelligence", html)
        self.assertIn("rep_test_123", html)
        self.assertIn("Global Procurement Fulfillment Summary", html)

        # Check KPI containers
        self.assertIn("kpi-total-orders", html)
        self.assertIn("kpi-on-time-pct", html)
        self.assertIn("kpi-financial-risk", html)
        self.assertIn("kpi-escalations-cnt", html)

        # Check Table and Cards containers
        self.assertIn("calls-table-body", html)
        self.assertIn("cards-view-section", html)

        # Check Modals
        self.assertIn("call-modal", html)
        self.assertIn("new-call-modal", html)
        self.assertIn("waveform-bars", html)

        # Check Embedded Data
        self.assertIn("PO-10001", html)
        self.assertIn("Beta Logistics Corp", html)
        self.assertIn("Gamma Wire Harness", html)
        self.assertIn("Delta Seals Inc", html)

    def test_reporter_export_html(self):
        """Validates that ProcurementReporter successfully writes HTML dashboard to disk."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            reporter = ProcurementReporter(output_dir=Path(tmp_dir))
            html_path = reporter.export_html(self.report, filename="dashboard.html")

            self.assertTrue(html_path.exists())
            self.assertEqual(html_path.name, "dashboard.html")
            content = html_path.read_text(encoding="utf-8")
            self.assertIn("CALL-E Supply Chain Intelligence", content)
            self.assertIn("rep_test_123", content)
            self.assertGreater(len(content), 1000)


if __name__ == "__main__":
    unittest.main()
