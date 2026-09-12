"""Tests for Pydantic models in src.models."""

import unittest
from src.models import (
    Supplier,
    PurchaseOrder,
    CallResult,
    FulfillmentStatus,
    DelayReasonCategory,
    BatchProcurementReport,
)


class TestModels(unittest.TestCase):

    def test_supplier_model(self):
        supp = Supplier(
            id="SUP-001",
            name="Test Supplier Corp",
            contact_name="Alice Smith",
            phone="+1-555-123-4567",
            email="alice@test.com",
        )
        self.assertEqual(supp.id, "SUP-001")
        self.assertEqual(supp.timezone, "America/New_York")

    def test_purchase_order_model(self):
        po = PurchaseOrder(
            order_id="PO-12345",
            supplier_id="SUP-001",
            item_description="Test Item",
            quantity=500,
            unit_cost_usd=10.0,
            total_value_usd=5000.0,
            committed_delivery_date="2026-09-25",
        )
        self.assertEqual(po.order_id, "PO-12345")
        self.assertEqual(po.quantity, 500)

    def test_call_result_model(self):
        cr = CallResult(
            call_id="call_test123",
            order_id="PO-12345",
            supplier_name="Test Supplier",
            contact_name="Alice Smith",
            phone_number="+1-555-123-4567",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.DELAYED,
            original_delivery_date="2026-09-25",
            revised_delivery_date="2026-09-30",
            delay_days=5,
            delay_category=DelayReasonCategory.RAW_MATERIAL_SHORTAGE,
            expedited_freight_cost_usd=500.0,
            estimated_financial_impact_usd=8000.0,
            escalation_required=True,
        )
        self.assertEqual(cr.fulfillment_status, FulfillmentStatus.DELAYED)
        self.assertTrue(cr.escalation_required)
        self.assertEqual(cr.delay_days, 5)
        self.assertIsNone(cr.recording_url)

    def test_call_result_with_recording_url(self):
        cr = CallResult(
            call_id="call_real_123",
            order_id="PO-88219",
            supplier_name="MicroSilicon Global Corp",
            contact_name="Dave Smith",
            phone_number="+1-563-281-3105",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.DELAYED,
            original_delivery_date="2026-09-15",
            revised_delivery_date="2026-09-22",
            delay_days=7,
            delay_category=DelayReasonCategory.RAW_MATERIAL_SHORTAGE,
            expedited_freight_cost_usd=1200.0,
            estimated_financial_impact_usd=11700.0,
            escalation_required=True,
            recording_url="/api/calls/call_real_123/audio",
        )
        self.assertEqual(cr.recording_url, "/api/calls/call_real_123/audio")
        data = cr.model_dump()
        self.assertEqual(data["recording_url"], "/api/calls/call_real_123/audio")
        # Roundtrip deserialization
        hydrated = CallResult(**data)
        self.assertEqual(hydrated.recording_url, "/api/calls/call_real_123/audio")


if __name__ == "__main__":
    unittest.main()
