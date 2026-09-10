"""
CALL-E Supply Chain MCP Server (Model Context Protocol).
Exposes CALL-E telephony agent capabilities to LLMs and Autonomous Agents via standard MCP protocol.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List

# Ensure repository root is in python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.models import Supplier, PurchaseOrder, CallResult
from src.calle_client import CalleSupplierAgentClient
from src.reporter import ProcurementReporter


class CalleProcurementMCPServer:
    """Standard JSON-RPC / MCP Server for CALL-E Supply Chain Operations."""

    def __init__(self, use_mock: bool = True):
        self.client = CalleSupplierAgentClient(use_mock=use_mock)
        self.reporter = ProcurementReporter()
        self.tools = [
            {
                "name": "calle_check_supplier_status",
                "description": "Trigger an outbound phone call via CALL-E to verify supplier fulfillment on a purchase order.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "supplier_id": {
                            "type": "string",
                            "description": "Unique supplier ID (e.g. SUP-101, SUP-102)"
                        },
                        "supplier_name": {
                            "type": "string",
                            "description": "Company name of the supplier"
                        },
                        "phone_number": {
                            "type": "string",
                            "description": "Telephone number formatted with country code (e.g. +1-555-014-9921)"
                        },
                        "contact_name": {
                            "type": "string",
                            "description": "Name of contact person / dispatcher",
                            "default": "Dispatcher"
                        },
                        "po_id": {
                            "type": "string",
                            "description": "Purchase order identifier (e.g. PO-88120)"
                        },
                        "item_description": {
                            "type": "string",
                            "description": "Description of contracted goods"
                        },
                        "target_date": {
                            "type": "string",
                            "description": "Committed delivery deadline (YYYY-MM-DD)"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity contracted",
                            "default": 1000
                        },
                        "live": {
                            "type": "boolean",
                            "description": "If true, initiates live telephone call. If false, executes high-fidelity simulation.",
                            "default": False
                        }
                    },
                    "required": ["supplier_id", "supplier_name", "phone_number", "po_id", "item_description", "target_date"]
                }
            },
            {
                "name": "calle_run_batch_procurement",
                "description": "Run batch outbound phone checks across all suppliers in a dataset and generate executive risk report.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_path": {
                            "type": "string",
                            "description": "Path to JSON file containing suppliers (defaults to data/suppliers.json)",
                            "default": "data/suppliers.json"
                        },
                        "live": {
                            "type": "boolean",
                            "description": "Whether to run live phone calls or zero-credit simulation",
                            "default": False
                        }
                    }
                }
            }
        ]

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the requested tool and returns the formatted result."""
        if name == "calle_check_supplier_status":
            supplier = Supplier(
                id=arguments["supplier_id"],
                name=arguments["supplier_name"],
                contact_name=arguments.get("contact_name", "Dispatcher"),
                phone=arguments["phone_number"],
            )
            order = PurchaseOrder(
                order_id=arguments["po_id"],
                supplier_id=arguments["supplier_id"],
                item_description=arguments["item_description"],
                quantity=arguments.get("quantity", 1000),
                unit_cost_usd=arguments.get("unit_cost_usd", 25.0),
                total_value_usd=arguments.get("total_value_usd", 25000.0),
                committed_delivery_date=arguments["target_date"],
            )
            is_live = arguments.get("live", False)
            client = self.client if not is_live else CalleSupplierAgentClient(use_mock=False)
            result = client.execute_call(supplier=supplier, order=order)
            return {
                "success": True,
                "result": result.model_dump()
            }

        elif name == "calle_run_batch_procurement":
            dataset_path = arguments.get("dataset_path", "data/suppliers.json")
            target_path = Path(dataset_path)
            if not target_path.is_absolute():
                target_path = BASE_DIR / target_path

            if not target_path.exists():
                return {"success": False, "error": f"Dataset file not found: {target_path}"}

            with open(target_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            is_live = arguments.get("live", False)
            client = self.client if not is_live else CalleSupplierAgentClient(use_mock=False)
            results: List[CallResult] = []

            for item in raw_data:
                s = Supplier(**item["supplier"])
                o = PurchaseOrder(**item["order"])
                scenario = item.get("mock_scenario")
                res = client.execute_call(supplier=s, order=o, scenario_override=scenario)
                results.append(res)

            report = self.reporter.generate_batch_report(results)
            return {
                "success": True,
                "report_id": report.report_id,
                "total_orders": report.total_orders_checked,
                "on_time": report.on_time_count,
                "delayed": report.delayed_count,
                "total_financial_exposure_usd": report.total_financial_risk_usd,
                "critical_escalations_count": len(report.critical_escalations)
            }

        else:
            return {"success": False, "error": f"Unknown tool: {name}"}

    def process_rpc_message(self, line: str) -> str:
        """Parses a single JSON-RPC line and returns JSON-RPC response."""
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": self.tools}
                })

            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                tool_result = self.handle_tool_call(tool_name, tool_args)
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(tool_result, indent=2)
                            }
                        ]
                    }
                })

            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                })

        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            })

    def run_stdio(self):
        """Runs the MCP server over standard input / output."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            resp = self.process_rpc_message(line)
            sys.stdout.write(resp + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    server = CalleProcurementMCPServer()
    server.run_stdio()
