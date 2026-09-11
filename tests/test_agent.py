"""Integration tests for agent execution and reporting pipeline."""

import unittest
import tempfile
from pathlib import Path

from src.models import Supplier, PurchaseOrder, FulfillmentStatus
from src.calle_client import CalleSupplierAgentClient
from src.reporter import ProcurementReporter


class TestAgentPipeline(unittest.TestCase):

    def setUp(self):
        self.client = CalleSupplierAgentClient(use_mock=True)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reporter = ProcurementReporter(output_dir=Path(self.temp_dir.name))

        self.test_supplier = Supplier(
            id="SUP-TEST",
            name="Test Components Inc",
            contact_name="Bob Vance",
            phone="+1-555-888-9999",
            email="bob@testcomponents.com",
        )
        self.test_order = PurchaseOrder(
            order_id="PO-99999",
            supplier_id="SUP-TEST",
            item_description="Test Sub-Assemblies",
            quantity=1000,
            unit_cost_usd=25.0,
            total_value_usd=25000.0,
            committed_delivery_date="2026-09-20",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_mock_call_on_time(self):
        scenario = {"status": "ON_TIME", "delay_days": 0, "reason": "Packed and ready."}
        result = self.client.execute_call(
            supplier=self.test_supplier,
            order=self.test_order,
            scenario_override=scenario,
        )
        self.assertEqual(result.fulfillment_status, FulfillmentStatus.ON_TIME)
        self.assertEqual(result.delay_days, 0)
        self.assertFalse(result.escalation_required)
        self.assertIn("Agent:", result.raw_transcript)

    def test_mock_call_delayed(self):
        scenario = {
            "status": "DELAYED",
            "revised_date": "2026-09-25",
            "delay_days": 5,
            "delay_category": "RAW_MATERIAL_SHORTAGE",
            "reason": "Resin shortage.",
            "expedited_freight_cost": 750.0,
            "escalation_name": "Bob Vance",
            "escalation_phone": "+1-555-888-9999",
        }
        result = self.client.execute_call(
            supplier=self.test_supplier,
            order=self.test_order,
            scenario_override=scenario,
        )
        self.assertEqual(result.fulfillment_status, FulfillmentStatus.DELAYED)
        self.assertEqual(result.delay_days, 5)
        self.assertTrue(result.escalation_required)
        self.assertEqual(result.expedited_freight_cost_usd, 750.0)

    def test_reporting_export(self):
        scenario_ot = {"status": "ON_TIME", "delay_days": 0}
        scenario_del = {"status": "DELAYED", "delay_days": 4, "revised_date": "2026-09-24"}

        r1 = self.client.execute_call(self.test_supplier, self.test_order, scenario_override=scenario_ot)
        r2 = self.client.execute_call(self.test_supplier, self.test_order, scenario_override=scenario_del)

        report = self.reporter.generate_batch_report([r1, r2])
        self.assertEqual(report.total_orders_checked, 2)
        self.assertEqual(report.on_time_count, 1)
        self.assertEqual(report.delayed_count, 1)
        self.assertEqual(report.on_time_percentage, 50.0)

        csv_path = self.reporter.export_csv([r1, r2], filename="test_report.csv")
        self.assertTrue(csv_path.exists())

        json_path = self.reporter.export_json(report, filename="test_report.json")
        self.assertTrue(json_path.exists())

        html_path = self.reporter.export_html(report, filename="test_report.html")
        self.assertTrue(html_path.exists())


if __name__ == "__main__":
    unittest.main()
