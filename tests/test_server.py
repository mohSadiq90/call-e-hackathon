"""Integration tests for FastAPI dashboard backend and REST API endpoints in src.server."""

import unittest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from src.server import app, state
from src.database import ProcurementDatabase
from src.reporter import ProcurementReporter


class TestServerAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.tmp_dir = tempfile.TemporaryDirectory()
        cls.tmp_db = Path(cls.tmp_dir.name) / "test_telephony.db"
        cls.orig_db = state.db
        cls.orig_reporter = state.reporter
        cls.orig_calls = list(state.call_results)
        cls.orig_report = state.report
        state.db = ProcurementDatabase(db_path=cls.tmp_db)
        state.reporter = ProcurementReporter(output_dir=Path(cls.tmp_dir.name))
        state.load_initial_data(force_recompute=True)

    @classmethod
    def tearDownClass(cls):
        state.db = cls.orig_db
        state.reporter = cls.orig_reporter
        state.call_results = cls.orig_calls
        state.report = cls.orig_report
        cls.tmp_dir.cleanup()

    def test_root_dashboard_html(self):
        """GET / should serve the interactive HTML dashboard."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers["content-type"])
        self.assertIn("<!DOCTYPE html>", resp.text)
        self.assertIn("CALL-E Supply Chain Intelligence", resp.text)

    def test_health_endpoints(self):
        """GET /health and /api/health should return system status."""
        for path in ["/health", "/api/health"]:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["service"], "call-e-procurement-dashboard")
            self.assertGreater(data["total_calls_loaded"], 0)

    def test_api_summary(self):
        """GET /api/summary should return aggregated executive KPIs."""
        resp = self.client.get("/api/summary")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total_orders_checked", data)
        self.assertIn("on_time_count", data)
        self.assertIn("delayed_count", data)
        self.assertIn("on_time_percentage", data)
        self.assertIn("total_financial_risk_usd", data)
        self.assertIn("call_records", data)

    def test_api_calls_list_and_filters(self):
        """GET /api/calls should list records with filtering support."""
        # Unfiltered list
        resp = self.client.get("/api/calls")
        self.assertEqual(resp.status_code, 200)
        calls = resp.json()
        self.assertIsInstance(calls, list)
        self.assertGreater(len(calls), 0)

        # Filter by status: ON_TIME
        resp_ot = self.client.get("/api/calls?status=ON_TIME")
        self.assertEqual(resp_ot.status_code, 200)
        calls_ot = resp_ot.json()
        self.assertTrue(all(c["fulfillment_status"] == "ON_TIME" for c in calls_ot))

        # Filter by status: DELAYED
        resp_del = self.client.get("/api/calls?status=DELAYED")
        self.assertEqual(resp_del.status_code, 200)
        calls_del = resp_del.json()
        self.assertTrue(all(c["fulfillment_status"] == "DELAYED" for c in calls_del))

        # Filter escalations only
        resp_esc = self.client.get("/api/calls?escalation_only=true")
        self.assertEqual(resp_esc.status_code, 200)
        calls_esc = resp_esc.json()
        self.assertTrue(all(c["escalation_required"] is True for c in calls_esc))

        # Search filter
        resp_search = self.client.get("/api/calls?search=PO-")
        self.assertEqual(resp_search.status_code, 200)
        self.assertGreater(len(resp_search.json()), 0)

    def test_api_get_call_by_id(self):
        """GET /api/calls/{call_id} should return single call detail or 404."""
        first_call = state.call_results[0]
        resp = self.client.get(f"/api/calls/{first_call.order_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["order_id"], first_call.order_id)
        self.assertIn("raw_transcript", data)

        # Not found case
        resp_404 = self.client.get("/api/calls/PO-NONEXISTENT-99999")
        self.assertEqual(resp_404.status_code, 404)

    def test_api_trigger_call(self):
        """POST /api/calls/trigger should execute an outbound call and append to state."""
        initial_count = len(state.call_results)
        payload = {
            "supplier_id": "SUP-TEST-NEW",
            "supplier_name": "Test Integration Supplier",
            "contact_name": "Sarah Miller",
            "phone_number": "+1-555-099-1234",
            "order_id": "PO-88888",
            "item_description": "High Precision Bearings",
            "quantity": 2500,
            "unit_cost_usd": 15.00,
            "total_value_usd": 37500.00,
            "committed_delivery_date": "2026-09-30", "authorization_confirmed": True, "destination_authorized": True,
            "destination_facility": "DC-04 Bentonville",
            "live": False, "authorization_confirmed": True, "destination_authorized": True,
            "mock_status": "ON_TIME",
            "delay_days": 0,
            "delay_category": "NONE",
            "delay_reason": "Packed and dispatched on schedule.",
        }
        resp = self.client.post("/api/calls/trigger", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["result"]["order_id"], "PO-88888")
        self.assertEqual(len(state.call_results), initial_count + 1)

    def test_api_trigger_call_default_live(self):
        """POST /api/calls/trigger without 'live' field should default to live=True."""
        from unittest.mock import patch
        from src.models import CallResult, FulfillmentStatus, DelayReasonCategory

        initial_count = len(state.call_results)
        payload = {
            "supplier_id": "SUP-TEST-DEFAULT-LIVE",
            "supplier_name": "Default Live Supplier",
            "contact_name": "David Clark",
            "phone_number": "+1-555-099-5678",
            "order_id": "PO-77777",
            "item_description": "Custom Sensor Assemblies",
            "quantity": 1500,
            "unit_cost_usd": 45.00,
            "total_value_usd": 67500.00,
            "committed_delivery_date": "2026-09-30", "authorization_confirmed": True, "destination_authorized": True,
            "destination_facility": "DC-02 Chicago",
        }
        mock_result = CallResult(
            call_id="call_default_live_123",
            order_id="PO-77777",
            supplier_name="Default Live Supplier",
            contact_name="David Clark",
            phone_number="+1-555-099-5678",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.ON_TIME,
            original_delivery_date="2026-09-30",
            revised_delivery_date="2026-09-30",
            delay_days=0,
            delay_category=DelayReasonCategory.NONE,
            delay_notes="Verified on schedule.",
            expedited_freight_cost_usd=0.0,
            estimated_financial_impact_usd=0.0,
            escalation_contact_name="David Clark",
            escalation_contact_phone="+1-555-099-5678",
            escalation_required=False,
            call_duration_seconds=75,
            raw_transcript="Agent: Hello.\nSupplier: On schedule.",
        )
        with patch("src.server.CALLE_API_KEY", "calle_live_server_default_key_7777"):
            with patch("src.server.CalleSupplierAgentClient") as mock_client_cls:
                mock_instance = mock_client_cls.return_value
                mock_instance.execute_call.return_value = mock_result

                resp = self.client.post("/api/calls/trigger", json=payload)
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                self.assertTrue(data["success"])
                self.assertTrue(data["is_live"])
                self.assertEqual(data["result"]["order_id"], "PO-77777")
                self.assertEqual(len(state.call_results), initial_count + 1)
                mock_client_cls.assert_called_with(api_key="calle_live_server_default_key_7777", use_mock=False)

    def test_api_trigger_call_live_missing_key_error(self):
        """POST /api/calls/trigger with live=True and no server API key should return 400."""
        from unittest.mock import patch

        payload = {
            "supplier_id": "SUP-NO-KEY",
            "supplier_name": "No Key Supplier",
            "contact_name": "Dave",
            "phone_number": "+1-555-099-0000",
            "order_id": "PO-NO-KEY",
            "item_description": "Parts",
            "quantity": 10,
            "committed_delivery_date": "2026-09-30", "authorization_confirmed": True, "destination_authorized": True,
            "live": True, "authorization_confirmed": True, "destination_authorized": True,
        }
        with patch("src.server.CALLE_API_KEY", ""):
            resp = self.client.post("/api/calls/trigger", json=payload)
            self.assertEqual(resp.status_code, 400)
            data = resp.json()
            self.assertIn("CALLE_API_KEY", data["detail"])

    def test_api_trigger_call_live_invalid_key_error(self):
        """POST /api/calls/trigger with invalid placeholder API key should return 400."""
        payload = {
            "supplier_id": "SUP-INVALID-KEY",
            "supplier_name": "Invalid Key Supplier",
            "contact_name": "Frank",
            "phone_number": "+1-555-099-0000",
            "order_id": "PO-KEY-ERR",
            "item_description": "Microchips",
            "quantity": 100,
            "committed_delivery_date": "2026-09-30", "authorization_confirmed": True, "destination_authorized": True,
            "live": True, "authorization_confirmed": True, "destination_authorized": True,
            "api_key": "your_calle_api_key_here",
        }
        resp = self.client.post("/api/calls/trigger", json=payload)
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn("CALLE_API_KEY", data["detail"])

    def test_api_trigger_call_live_custom_key_dispatch(self):
        """POST /api/calls/trigger with custom valid API key should initiate live dispatch."""
        from unittest.mock import patch
        from src.models import CallResult, FulfillmentStatus, DelayReasonCategory

        mock_result = CallResult(
            call_id="call_custom_key_123",
            order_id="PO-CUSTOM-KEY",
            supplier_name="Live Custom Supplier",
            contact_name="Alice",
            phone_number="+15632813105",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.ON_TIME,
            original_delivery_date="2026-09-30",
            revised_delivery_date="2026-09-30",
            delay_days=0,
            delay_category=DelayReasonCategory.NONE,
            delay_notes="Verified via live CALL-E network.",
            expedited_freight_cost_usd=0.0,
            estimated_financial_impact_usd=0.0,
            escalation_contact_name="Alice",
            escalation_contact_phone="+15632813105",
            escalation_required=False,
            call_duration_seconds=92,
            raw_transcript="Agent: Testing custom key.\nSupplier: Confirmed.",
        )

        with patch("src.server.CalleSupplierAgentClient") as mock_client_cls:
            mock_instance = mock_client_cls.return_value
            mock_instance.execute_call.return_value = mock_result

            payload = {
                "supplier_id": "SUP-LIVE-CUSTOM",
                "supplier_name": "Live Custom Supplier",
                "contact_name": "Alice",
                "phone_number": "+1-563-281-3105",
                "order_id": "PO-CUSTOM-KEY",
                "item_description": "Laser Optics",
                "quantity": 500,
                "committed_delivery_date": "2026-09-30", "authorization_confirmed": True, "destination_authorized": True,
                "live": True, "authorization_confirmed": True, "destination_authorized": True,
                "api_key": "calle_live_custom_secret_12345",
            }
            resp = self.client.post("/api/calls/trigger", json=payload)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertTrue(data["success"])
            self.assertTrue(data["is_live"])
            self.assertEqual(data["result"]["call_id"], "call_custom_key_123")
            mock_client_cls.assert_called_with(api_key="calle_live_custom_secret_12345", use_mock=False)

    def test_api_trigger_call_live_uses_server_environment_key(self):
        """POST /api/calls/trigger without api_key in payload uses server environment CALLE_API_KEY."""
        from unittest.mock import patch
        from src.models import CallResult, FulfillmentStatus, DelayReasonCategory

        mock_result = CallResult(
            call_id="call_env_key_456",
            order_id="PO-ENV-KEY",
            supplier_name="Server Env Supplier",
            contact_name="Bob",
            phone_number="+15632813105",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.ON_TIME,
            original_delivery_date="2026-09-30",
            revised_delivery_date="2026-09-30",
            delay_days=0,
            delay_category=DelayReasonCategory.NONE,
            delay_notes="Verified via live CALL-E network with server key.",
            expedited_freight_cost_usd=0.0,
            estimated_financial_impact_usd=0.0,
            escalation_contact_name="Bob",
            escalation_contact_phone="+15632813105",
            escalation_required=False,
            call_duration_seconds=85,
            raw_transcript="Agent: Testing server env key.\nSupplier: Confirmed on schedule.",
        )

        with patch("src.server.CALLE_API_KEY", "calle_live_server_env_key_99999"):
            with patch("src.server.CalleSupplierAgentClient") as mock_client_cls:
                mock_instance = mock_client_cls.return_value
                mock_instance.execute_call.return_value = mock_result

                # No api_key field in payload (exactly as sent by the updated form)
                payload = {
                    "supplier_id": "SUP-LIVE-ENV",
                    "supplier_name": "Server Env Supplier",
                    "contact_name": "Bob",
                    "phone_number": "+1-563-281-3105",
                    "order_id": "PO-ENV-KEY",
                    "item_description": "Laser Optics",
                    "quantity": 500,
                    "committed_delivery_date": "2026-09-30", "authorization_confirmed": True, "destination_authorized": True,
                    "live": True, "authorization_confirmed": True, "destination_authorized": True,
                }
                resp = self.client.post("/api/calls/trigger", json=payload)
                self.assertEqual(resp.status_code, 200)
                data = resp.json()
                self.assertTrue(data["success"])
                self.assertTrue(data["is_live"])
                self.assertEqual(data["result"]["call_id"], "call_env_key_456")
                mock_client_cls.assert_called_with(api_key="calle_live_server_env_key_99999", use_mock=False)

    def test_api_export_csv(self):
        """GET /api/export/csv should stream CSV data."""
        resp = self.client.get("/api/export/csv")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp.headers["content-type"])
        self.assertIn("order_id", resp.text)

    def test_api_export_json(self):
        """GET /api/export/json should stream JSON data."""
        resp = self.client.get("/api/export/json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/json", resp.headers["content-type"])
        data = resp.json()
        self.assertIn("call_records", data)

    def test_api_trigger_batch_workflow(self):
        """POST /api/workflow/trigger-batch should run batch verification and return results."""
        initial_count = len(state.call_results)
        payload = {
            "category": "Critical Electronics",
            "max_orders": 2,
            "live": False, "authorization_confirmed": True, "destination_authorized": True,
        }
        resp = self.client.post("/api/workflow/trigger-batch", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])
        self.assertIn("processed_count", data)
        self.assertGreater(data["processed_count"], 0)
        self.assertEqual(len(state.call_results), initial_count + data["processed_count"])

    def test_api_db_stats(self):
        """GET /api/db/stats should return SQLite database metrics and table names."""
        resp = self.client.get("/api/db/stats")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("database_path", data)
        self.assertIn("total_calls", data)
        self.assertIn("tables", data)
        self.assertIn("call_records", data["tables"])
        self.assertIn("suppliers", data["tables"])
        self.assertIn("purchase_orders", data["tables"])
        self.assertGreaterEqual(data["total_calls"], 1)

    def test_verified_real_call_loaded(self):
        """Verified real call (call_BX2osyVHhnrQgDngurhn8w) must be loaded with recording_url."""
        resp = self.client.get("/api/calls/call_BX2osyVHhnrQgDngurhn8w")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["call_id"], "call_BX2osyVHhnrQgDngurhn8w")
        self.assertEqual(data["order_id"], "PO-88219")
        self.assertIsNotNone(data.get("recording_url"))
        self.assertIn("/audio", data["recording_url"])

    def test_get_call_audio(self):
        """GET /api/calls/{call_id}/audio should serve playable telephony audio."""
        resp = self.client.get("/api/calls/call_BX2osyVHhnrQgDngurhn8w/audio")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("audio/", resp.headers["content-type"])
        self.assertGreater(len(resp.content), 1000)

    def test_get_call_recording_meta(self):
        """GET /api/calls/{call_id}/recording should return recording status and URL."""
        resp = self.client.get("/api/calls/call_BX2osyVHhnrQgDngurhn8w/recording")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["call_id"], "call_BX2osyVHhnrQgDngurhn8w")
        self.assertTrue(data["has_recording"])
        self.assertIsNotNone(data["recording_url"])

    def test_api_calls_recording_only_filter(self):
        """GET /api/calls?recording_only=true should return only calls with audio recording."""
        resp = self.client.get("/api/calls?recording_only=true")
        self.assertEqual(resp.status_code, 200)
        calls = resp.json()
        self.assertGreaterEqual(len(calls), 1)
        self.assertTrue(all(bool(c.get("recording_url")) for c in calls))

    def test_api_calls_search_by_phone_and_call_id(self):
        """GET /api/calls?search=... should match phone numbers (formatted/digits) and call IDs."""
        # 1. Search by formatted phone number
        resp1 = self.client.get("/api/calls?search=563-281-3105")
        self.assertEqual(resp1.status_code, 200)
        orders1 = [c["order_id"] for c in resp1.json()]
        self.assertIn("PO-88219", orders1)

        # 2. Search by raw phone digits
        resp2 = self.client.get("/api/calls?search=5632813105")
        self.assertEqual(resp2.status_code, 200)
        orders2 = [c["order_id"] for c in resp2.json()]
        self.assertIn("PO-88219", orders2)

        # 3. Search by call_id substring
        resp3 = self.client.get("/api/calls?search=BX2osy")
        self.assertEqual(resp3.status_code, 200)
        orders3 = [c["order_id"] for c in resp3.json()]
        self.assertIn("PO-88219", orders3)

        # 4. Search by PO ID
        resp4 = self.client.get("/api/calls?search=PO-88219")
        self.assertEqual(resp4.status_code, 200)
        orders4 = [c["order_id"] for c in resp4.json()]
        self.assertIn("PO-88219", orders4)

    def test_health_head_method_and_telephony_readiness(self):
        """HEAD /health and GET /health should succeed and return database count and telephony readiness."""
        head_resp = self.client.head("/health")
        self.assertEqual(head_resp.status_code, 200)

        get_resp = self.client.get("/health")
        self.assertEqual(get_resp.status_code, 200)
        data = get_resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database_records", data)
        self.assertIn("has_calle_api_key", data)
        self.assertIn("telephony_mode", data)


if __name__ == "__main__":
    unittest.main()


