"""
Unit and Integration Tests for SQLite Database Persistence in src.database.
Validates table creation, CRUD operations, query filtering, pagination,
model fidelity, and backend server state integration.
"""

import os
import tempfile
import unittest
from pathlib import Path

from src.models import (
    Supplier,
    PurchaseOrder,
    CallResult,
    FulfillmentStatus,
    DelayReasonCategory,
)
from src.database import ProcurementDatabase


class TestProcurementDatabaseUnit(unittest.TestCase):
    """Unit tests for ProcurementDatabase SQLite operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_procurement.db"
        self.db = ProcurementDatabase(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_sample_call(
        self,
        call_id: str = "CALL-TEST-001",
        order_id: str = "PO-10001",
        supplier_name: str = "Apex Logistics",
        status: FulfillmentStatus = FulfillmentStatus.ON_TIME,
        delay_days: int = 0,
        delay_category: DelayReasonCategory = DelayReasonCategory.NONE,
        escalation: bool = False,
        financial_impact: float = 0.0,
    ) -> CallResult:
        return CallResult(
            call_id=call_id,
            order_id=order_id,
            supplier_name=supplier_name,
            contact_name="Sarah Jenkins",
            phone_number="+1-555-019-2831",
            call_status="COMPLETED",
            fulfillment_status=status,
            original_delivery_date="2026-09-20",
            revised_delivery_date="2026-09-20" if delay_days == 0 else "2026-09-25",
            delay_days=delay_days,
            delay_category=delay_category,
            delay_notes="Test operational note.",
            expedited_freight_cost_usd=500.0 if delay_days > 0 else 0.0,
            estimated_financial_impact_usd=financial_impact,
            escalation_contact_name="Director Dave" if escalation else None,
            escalation_contact_phone="+1-555-999-0000" if escalation else None,
            escalation_required=escalation,
            call_duration_seconds=78,
            timestamp="2026-09-12T12:00:00Z",
            raw_transcript="Agent: Verification.\nSupplier: Confirmed.",
        )

    def test_database_initialization(self):
        """Database file and required tables/indexes must be created properly."""
        self.assertTrue(self.db_path.exists())
        tables = self.db.get_table_names()
        self.assertIn("call_records", tables)
        self.assertIn("suppliers", tables)
        self.assertIn("purchase_orders", tables)

    def test_upsert_and_get_by_id(self):
        """Upserting a CallResult should persist and retrieve with full fidelity."""
        call = self._create_sample_call()
        self.db.upsert_call_result(call)

        retrieved = self.db.get_call_by_id("CALL-TEST-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.call_id, "CALL-TEST-001")
        self.assertEqual(retrieved.order_id, "PO-10001")
        self.assertEqual(retrieved.supplier_name, "Apex Logistics")
        self.assertEqual(retrieved.fulfillment_status, FulfillmentStatus.ON_TIME)
        self.assertEqual(retrieved.delay_days, 0)
        self.assertEqual(retrieved.delay_category, DelayReasonCategory.NONE)
        self.assertEqual(retrieved.call_duration_seconds, 78)
        self.assertEqual(retrieved.raw_transcript, "Agent: Verification.\nSupplier: Confirmed.")

    def test_get_by_order_id(self):
        """Should retrieve call record by purchase order ID."""
        call = self._create_sample_call(order_id="PO-UNIQUE-99")
        self.db.upsert_call_result(call)

        retrieved = self.db.get_call_by_order_id("PO-UNIQUE-99")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.order_id, "PO-UNIQUE-99")

    def test_upsert_updates_existing_record(self):
        """Re-inserting same call_id with updated values must update existing row."""
        call = self._create_sample_call(call_id="CALL-UPDATE-1", status=FulfillmentStatus.ON_TIME)
        self.db.upsert_call_result(call)
        self.assertEqual(self.db.count_calls(), 1)

        # Update call to delayed
        updated_call = self._create_sample_call(
            call_id="CALL-UPDATE-1",
            status=FulfillmentStatus.DELAYED,
            delay_days=5,
            delay_category=DelayReasonCategory.LOGISTICS_PORT_CONGESTION,
            financial_impact=8000.0,
        )
        self.db.upsert_call_result(updated_call)
        self.assertEqual(self.db.count_calls(), 1)

        retrieved = self.db.get_call_by_id("CALL-UPDATE-1")
        self.assertEqual(retrieved.fulfillment_status, FulfillmentStatus.DELAYED)
        self.assertEqual(retrieved.delay_days, 5)
        self.assertEqual(retrieved.delay_category, DelayReasonCategory.LOGISTICS_PORT_CONGESTION)
        self.assertEqual(retrieved.estimated_financial_impact_usd, 8000.0)

    def test_batch_upsert_and_count(self):
        """Batch upserting should insert multiple records efficiently."""
        calls = [
            self._create_sample_call(call_id=f"CALL-BATCH-{i}", order_id=f"PO-BATCH-{i}")
            for i in range(10)
        ]
        count_inserted = self.db.upsert_call_results_batch(calls)
        self.assertEqual(count_inserted, 10)
        self.assertEqual(self.db.count_calls(), 10)

    def test_query_filtering(self):
        """Queries should support filtering by status, category, and escalation."""
        call1 = self._create_sample_call(
            call_id="C-1", status=FulfillmentStatus.ON_TIME, escalation=False
        )
        call2 = self._create_sample_call(
            call_id="C-2",
            status=FulfillmentStatus.DELAYED,
            delay_days=4,
            delay_category=DelayReasonCategory.RAW_MATERIAL_SHORTAGE,
            escalation=True,
        )
        call3 = self._create_sample_call(
            call_id="C-3",
            status=FulfillmentStatus.PARTIAL_DISPATCH,
            delay_days=2,
            delay_category=DelayReasonCategory.LOGISTICS_PORT_CONGESTION,
            escalation=False,
        )
        self.db.upsert_call_results_batch([call1, call2, call3])

        # Filter status
        delayed = self.db.list_calls(status="DELAYED")
        self.assertEqual(len(delayed), 1)
        self.assertEqual(delayed[0].call_id, "C-2")

        # Filter category
        shortage = self.db.list_calls(category="RAW_MATERIAL_SHORTAGE")
        self.assertEqual(len(shortage), 1)
        self.assertEqual(shortage[0].call_id, "C-2")

        # Filter escalation
        escalations = self.db.list_calls(escalation_only=True)
        self.assertEqual(len(escalations), 1)
        self.assertEqual(escalations[0].call_id, "C-2")

    def test_search_and_pagination(self):
        """Search query matching and pagination limit/offset."""
        calls = [
            self._create_sample_call(
                call_id=f"C-SEARCH-{i}",
                order_id=f"PO-SRCH-{i:03d}",
                supplier_name="Global Microelectronics" if i < 3 else "Acme Fasteners",
            )
            for i in range(6)
        ]
        self.db.upsert_call_results_batch(calls)

        # Search supplier name
        results = self.db.list_calls(search="Microelectronics")
        self.assertEqual(len(results), 3)

        # Pagination
        p1 = self.db.list_calls(limit=2, offset=0)
        p2 = self.db.list_calls(limit=2, offset=2)
        self.assertEqual(len(p1), 2)
        self.assertEqual(len(p2), 2)
        self.assertNotEqual(p1[0].call_id, p2[0].call_id)

    def test_supplier_and_po_storage(self):
        """Saving suppliers and purchase orders should succeed."""
        supp = Supplier(
            id="SUP-TEST-1",
            name="Test Supplier Corp",
            contact_name="Alice",
            phone="+1-555-123-4567",
            email="alice@testsupplier.com",
            category="Semiconductors",
        )
        po = PurchaseOrder(
            order_id="PO-TEST-1",
            supplier_id="SUP-TEST-1",
            item_description="Precision Sensors",
            quantity=1000,
            unit_cost_usd=45.0,
            total_value_usd=45000.0,
            committed_delivery_date="2026-09-30",
        )

        self.db.save_supplier(supp)
        self.db.save_purchase_order(po)

        retrieved_supp = self.db.get_supplier("SUP-TEST-1")
        self.assertIsNotNone(retrieved_supp)
        self.assertEqual(retrieved_supp.name, "Test Supplier Corp")

        retrieved_po = self.db.get_purchase_order("PO-TEST-1")
        self.assertIsNotNone(retrieved_po)
        self.assertEqual(retrieved_po.total_value_usd, 45000.0)

    def test_clear_all(self):
        """Clearing calls should remove all records."""
        self.db.upsert_call_result(self._create_sample_call())
        self.assertEqual(self.db.count_calls(), 1)
        self.db.clear_all_calls()
        self.assertEqual(self.db.count_calls(), 0)

    def test_recording_url_persistence(self):
        """Call results with recording_url should persist and reload properly."""
        sample = self._create_sample_call(call_id="CALL-REC-001")
        sample.recording_url = "/api/calls/CALL-REC-001/audio"
        self.db.upsert_call_result(sample)

        loaded = self.db.get_call_by_id("CALL-REC-001")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.recording_url, "/api/calls/CALL-REC-001/audio")

        # Update recording_url
        sample.recording_url = "https://api.heycall-e.com/v1/calls/call_test/recording"
        self.db.upsert_call_result(sample)
        reloaded = self.db.get_call_by_id("CALL-REC-001")
        self.assertEqual(reloaded.recording_url, "https://api.heycall-e.com/v1/calls/call_test/recording")

    def test_recording_only_filtering(self):
        """list_calls with recording_only=True should filter out records without audio."""
        c1 = self._create_sample_call(call_id="CALL-WITH-REC")
        c1.recording_url = "/api/calls/CALL-WITH-REC/audio"

        c2 = self._create_sample_call(call_id="CALL-WITHOUT-REC")
        c2.recording_url = None

        self.db.upsert_call_result(c1)
        self.db.upsert_call_result(c2)

        all_calls = self.db.list_calls()
        self.assertEqual(len(all_calls), 2)

        rec_calls = self.db.list_calls(recording_only=True)
        self.assertEqual(len(rec_calls), 1)
        self.assertEqual(rec_calls[0].call_id, "CALL-WITH-REC")

    def test_database_migration_adds_recording_url(self):
        """Existing legacy database without recording_url column should auto-migrate."""
        import sqlite3
        legacy_db_path = Path(self.temp_dir.name) / "legacy_v1.db"
        with sqlite3.connect(str(legacy_db_path)) as conn:
            conn.execute("""
                CREATE TABLE call_records (
                    call_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    supplier_name TEXT NOT NULL,
                    contact_name TEXT NOT NULL,
                    phone_number TEXT NOT NULL,
                    call_status TEXT NOT NULL,
                    fulfillment_status TEXT NOT NULL,
                    original_delivery_date TEXT NOT NULL,
                    revised_delivery_date TEXT,
                    delay_days INTEGER DEFAULT 0,
                    delay_category TEXT DEFAULT 'NONE',
                    delay_notes TEXT,
                    expedited_freight_cost_usd REAL DEFAULT 0.0,
                    estimated_financial_impact_usd REAL DEFAULT 0.0,
                    escalation_contact_name TEXT,
                    escalation_contact_phone TEXT,
                    escalation_required INTEGER DEFAULT 0,
                    call_duration_seconds INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    raw_transcript TEXT DEFAULT '',
                    data_json TEXT NOT NULL
                );
            """)
            conn.commit()

        # Connect with ProcurementDatabase, should trigger migration without error
        migrated_db = ProcurementDatabase(db_path=legacy_db_path)
        with migrated_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(call_records);")
            col_names = [r["name"] for r in cursor.fetchall()]
            self.assertIn("recording_url", col_names)


class TestDatabaseServerIntegration(unittest.TestCase):
    """Integration tests verifying server state synchronization with SQLite."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "server_integration.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_server_state_sqlite_roundtrip(self):
        """DashboardBackendState should initialize and persist through SQLite."""
        from src.server import DashboardBackendState
        from config.settings import DATA_DIR

        test_state = DashboardBackendState(db_path=self.db_path)
        # Use small suppliers.json for fast test run
        small_dataset = DATA_DIR / "suppliers.json"
        test_state.load_initial_data(dataset_path=small_dataset, force_recompute=True)

        self.assertGreaterEqual(len(test_state.call_results), 5)
        self.assertGreaterEqual(test_state.db.count_calls(), 5)

        # Simulate fresh server reload with same SQLite database (without recomputing)
        fresh_state = DashboardBackendState(db_path=self.db_path)
        fresh_state.load_initial_data(dataset_path=small_dataset, force_recompute=False)

        # Should load directly from SQLite
        self.assertEqual(len(fresh_state.call_results), len(test_state.call_results))
        self.assertEqual(fresh_state.report.total_orders_checked, len(test_state.call_results))


if __name__ == "__main__":
    unittest.main()
