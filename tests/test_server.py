"""Integration tests for FastAPI dashboard backend and REST API endpoints in src.server."""

import unittest
import json
from fastapi.testclient import TestClient

from src.server import app, state


class TestServerAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        state.load_initial_data()

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
            "committed_delivery_date": "2026-09-28",
            "destination_facility": "DC-04 Bentonville",
            "live": False,
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
            "live": False,
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


if __name__ == "__main__":
    unittest.main()


