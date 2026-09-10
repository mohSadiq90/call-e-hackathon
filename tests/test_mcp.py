import unittest
import json
from src.mcp_server import CalleProcurementMCPServer


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = CalleProcurementMCPServer()

    def test_tools_list(self):
        req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        resp_str = self.server.process_rpc_message(req)
        resp = json.loads(resp_str)
        self.assertEqual(resp["id"], 1)
        self.assertIn("result", resp)
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("calle_check_supplier_status", tool_names)
        self.assertIn("calle_run_batch_procurement", tool_names)

    def test_tool_call_single_supplier(self):
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "calle_check_supplier_status",
                "arguments": {
                    "supplier_id": "SUP-101",
                    "supplier_name": "Apex Microelectronics Inc.",
                    "phone_number": "+1-555-014-9921",
                    "po_id": "PO-91042",
                    "item_description": "Microcontroller IC units",
                    "target_date": "2026-09-18",
                    "live": False
                }
            }
        })
        resp_str = self.server.process_rpc_message(req)
        resp = json.loads(resp_str)
        self.assertEqual(resp["id"], 2)
        content = json.loads(resp["result"]["content"][0]["text"])
        self.assertTrue(content["success"])
        self.assertEqual(content["result"]["order_id"], "PO-91042")
        self.assertEqual(content["result"]["supplier_name"], "Apex Microelectronics Inc.")

    def test_tool_call_batch_procurement(self):
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "calle_run_batch_procurement",
                "arguments": {
                    "dataset_path": "data/suppliers.json",
                    "live": False
                }
            }
        })
        resp_str = self.server.process_rpc_message(req)
        resp = json.loads(resp_str)
        self.assertEqual(resp["id"], 3)
        content = json.loads(resp["result"]["content"][0]["text"])
        self.assertTrue(content["success"])
        self.assertEqual(content["total_orders"], 5)
        self.assertEqual(content["on_time"], 2)
        self.assertEqual(content["delayed"], 3)


if __name__ == "__main__":
    unittest.main()
