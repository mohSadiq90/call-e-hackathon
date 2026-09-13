"""
Backend HTTP Server and REST API for CALL-E Supply Chain Intelligence Dashboard.
Serves the intuitive HTML dashboard, provides RESTful endpoints to query call records,
filter executive KPIs, and trigger live or simulated supplier verification calls.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field

from config.settings import (
    DATA_DIR,
    OUTPUT_DIR,
    DATABASE_PATH,
    CALLE_API_KEY,
    ENABLE_MOCK_SIMULATOR,
)
from src.database import ProcurementDatabase
from src.models import (
    Supplier,
    PurchaseOrder,
    CallResult,
    FulfillmentStatus,
    DelayReasonCategory,
    BatchProcurementReport,
)
from src.calle_client import CalleSupplierAgentClient
from src.reporter import ProcurementReporter
from src.html_dashboard import render_html_dashboard

# FastAPI application instance
app = FastAPI(
    title="CALL-E Supply Chain Intelligence API",
    description="Enterprise Telephony Backend & Real-time Operations Dashboard",
    version="1.0.0",
)

# Global State Container
class DashboardBackendState:
    def __init__(self, db_path: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.data_path: Path = DATA_DIR / "suppliers_enterprise_50.json"
        if not self.data_path.exists():
            self.data_path = DATA_DIR / "suppliers.json"
        self.reporter = ProcurementReporter(output_dir=output_dir or OUTPUT_DIR)
        self.client = CalleSupplierAgentClient(use_mock=True)
        self.db = ProcurementDatabase(db_path=db_path or DATABASE_PATH)
        self.call_results: List[CallResult] = []
        self.report: Optional[BatchProcurementReport] = None

    def _sync_verified_real_call(self):
        """Ensures the verified real Call-E call (call_BX2osyVHhnrQgDngurhn8w) is always included with its recording URL."""
        real_call_file = DATA_DIR / "real_call_BX2osyVHhnrQgDngurhn8w.json"
        if not real_call_file.exists():
            return
        try:
            with open(real_call_file, "r", encoding="utf-8") as f:
                real_task_data = json.load(f)
            supp = Supplier(
                id="SUP-REAL-001",
                name="MicroSilicon Global Corp",
                contact_name="Dave / Fulfillment Coordinator",
                phone="+1-563-281-3105",
                category="Critical Electronics",
            )
            po = PurchaseOrder(
                order_id="PO-88219",
                supplier_id="SUP-REAL-001",
                item_description="5,000 Microcontroller Units",
                quantity=5000,
                unit_cost_usd=28.50,
                total_value_usd=142500.00,
                committed_delivery_date="2026-09-15",
                destination_facility="DC-04 Bentonville Facility",
            )
            real_result = CalleSupplierAgentClient.from_calle_api_task(
                task_data=real_task_data,
                order=po,
                supplier=supp,
                recording_url="/api/calls/call_BX2osyVHhnrQgDngurhn8w/audio",
            )
            existing_ids = {c.call_id for c in self.call_results}
            order_match_idx = next((i for i, c in enumerate(self.call_results) if c.order_id == real_result.order_id), None)
            if real_result.call_id in existing_ids:
                for idx, c in enumerate(self.call_results):
                    if c.call_id == real_result.call_id:
                        self.call_results[idx] = real_result
                        self.db.upsert_call_result(real_result)
                        break
            elif order_match_idx is not None:
                self.call_results[order_match_idx] = real_result
                self.db.upsert_call_result(real_result)
            else:
                self.call_results.insert(0, real_result)
                self.db.upsert_call_result(real_result)
        except Exception as e:
            print(f"[SERVER] Note on loading real call: {e}")

    def load_initial_data(self, dataset_path: Optional[Path] = None, force_recompute: bool = False):
        if dataset_path:
            self.data_path = dataset_path

        # 1. Check SQLite database first if not force_recompute
        if not force_recompute and self.db.count_calls() > 0:
            stored_calls = self.db.load_all_calls()
            self.call_results = stored_calls
            self._sync_verified_real_call()
            self.report = self.reporter.generate_batch_report(self.call_results)
            print(f"[SERVER] Loaded {len(self.call_results)} call records from SQLite DB: {self.db.db_path}")
            return

        # 2. If existing report JSON exists and not forcing recompute, load from cache and sync to DB
        report_cache = OUTPUT_DIR / "procurement_status_report.json"
        if report_cache.exists() and not force_recompute:
            try:
                with open(report_cache, "r", encoding="utf-8") as f:
                    cache_dict = json.load(f)
                    self.report = BatchProcurementReport(**cache_dict)
                    self.call_results = self.report.call_records
                    self._sync_verified_real_call()
                    self.db.upsert_call_results_batch(self.call_results)
                    print(f"[SERVER] Loaded {len(self.call_results)} call records from cache and synced to SQLite DB: {self.db.db_path}")
                    return
            except Exception as e:
                print(f"[SERVER] Failed to load cache ({e}), recomputing from dataset...")

        # 3. Otherwise execute mock calls from dataset and persist to SQLite
        if not self.data_path.exists():
            print(f"[SERVER WARN] Data path {self.data_path} not found, falling back to suppliers.json")
            self.data_path = DATA_DIR / "suppliers.json"

        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        print(f"[SERVER] Processing {len(raw_data)} supplier orders from {self.data_path.name}...")
        if force_recompute:
            self.db.clear_all()
        self.db.save_suppliers_and_orders(raw_data)

        results = []
        for item in raw_data:
            supplier = Supplier(**item["supplier"])
            order = PurchaseOrder(**item["order"])
            mock_scenario = item.get("mock_scenario", {})
            res = self.client.execute_call(
                supplier=supplier,
                order=order,
                scenario_override=mock_scenario,
            )
            results.append(res)

        self.call_results = results
        self._sync_verified_real_call()
        # Persist all records to SQLite database
        self.db.upsert_call_results_batch(self.call_results)

        self.report = self.reporter.generate_batch_report(self.call_results)
        self.reporter.export_csv(self.call_results)
        self.reporter.export_json(self.report)
        self.reporter.export_html(self.report)
        print(f"[SERVER] Initialized {len(self.call_results)} calls into SQLite DB. Dashboard ready.")


state = DashboardBackendState()


class TriggerCallPayload(BaseModel):
    supplier_id: str = "SUP-CUSTOM"
    supplier_name: str = "Custom Global Logistics"
    contact_name: str = "Operations Lead"
    phone_number: str = "+1-555-010-0000"
    order_id: str = "PO-99500"
    item_description: str = "Critical Electronics Components"
    quantity: int = 5000
    unit_cost_usd: float = 12.50
    total_value_usd: float = 62500.00
    committed_delivery_date: str = "2026-09-25"
    destination_facility: str = "DC-04 Bentonville Facility"
    live: bool = True
    api_key: Optional[str] = None
    mock_status: Optional[str] = "ON_TIME"
    delay_days: Optional[int] = 0
    delay_category: Optional[str] = "NONE"
    delay_reason: Optional[str] = "Shipment on schedule."
    expedited_freight_cost: Optional[float] = 0.0
    recording_url: Optional[str] = None


class TriggerBatchWorkflowPayload(BaseModel):
    category: Optional[str] = "ALL"
    max_orders: Optional[int] = 5
    live: bool = True
    api_key: Optional[str] = None



@app.on_event("startup")
def startup_event():
    """Initializes dataset on server startup."""
    state.load_initial_data()


@app.get("/", response_class=HTMLResponse)
def get_dashboard_html():
    """Serves the intuitive, interactive executive HTML dashboard."""
    if not state.report:
        state.load_initial_data()
    html = render_html_dashboard(state.report)
    return HTMLResponse(content=html, status_code=200)


@app.get("/health")
@app.head("/health")
@app.get("/api/health")
@app.head("/api/health")
def health_check():
    """Health check endpoint with SQLite database status and telephony readiness."""
    if not state.call_results:
        state.load_initial_data()
    has_valid_api_key = bool(
        CALLE_API_KEY
        and CALLE_API_KEY not in ("your_calle_api_key_here", "calle_live_your_api_key_here")
    )
    return {
        "status": "healthy",
        "service": "call-e-procurement-dashboard",
        "version": "1.0.0",
        "database": "sqlite",
        "database_records": state.db.count_calls(),
        "total_calls_loaded": len(state.call_results),
        "has_calle_api_key": has_valid_api_key,
        "telephony_mode": "live_ready" if has_valid_api_key else "simulation_fallback",
    }


@app.get("/api/db/stats")
def get_db_stats():
    """Returns SQLite database storage statistics and table structure."""
    return {
        "database_path": str(state.db.db_path),
        "total_calls": state.db.count_calls(),
        "tables": state.db.get_table_names(),
        "suppliers_count": len(state.db.list_suppliers()),
    }


@app.get("/api/summary", response_model=Dict[str, Any])
def get_procurement_summary():
    """Returns aggregated executive KPI metrics and summary report."""
    if not state.report:
        state.load_initial_data()
    return state.report.model_dump()


@app.get("/api/calls", response_model=List[Dict[str, Any]])
def list_calls(
    status: Optional[str] = Query(None, description="Filter by status: ON_TIME, DELAYED, PARTIAL_DISPATCH, UNREACHABLE"),
    search: Optional[str] = Query(None, description="Search query string"),
    category: Optional[str] = Query(None, description="Filter by delay root cause category"),
    escalation_only: Optional[bool] = Query(False, description="Filter only critical escalations"),
    recording_only: Optional[bool] = Query(False, description="Filter only calls with live audio recordings"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Queries call records with optional filtering and pagination."""
    if not state.call_results:
        state.load_initial_data()
    records = state.call_results

    if status and status.upper() != "ALL":
        records = [r for r in records if r.fulfillment_status.value.upper() == status.upper()]

    if category and category.upper() != "ALL":
        records = [r for r in records if r.delay_category.value.upper() == category.upper()]

    if escalation_only:
        records = [r for r in records if r.escalation_required]

    if recording_only:
        records = [r for r in records if r.recording_url]

    if search:
        q = search.lower().strip()
        q_digits = re.sub(r"\D", "", q)

        def _matches(r: CallResult) -> bool:
            if (
                q in r.order_id.lower()
                or q in r.supplier_name.lower()
                or q in r.contact_name.lower()
                or q in r.phone_number.lower()
                or q in r.call_id.lower()
                or q in (r.escalation_contact_name or "").lower()
                or q in (r.escalation_contact_phone or "").lower()
                or q in (r.delay_notes or "").lower()
                or q in r.delay_category.value.lower()
            ):
                return True
            if len(q_digits) >= 3:
                phone_digits = re.sub(r"\D", "", r.phone_number)
                esc_digits = re.sub(r"\D", "", r.escalation_contact_phone or "")
                if q_digits in phone_digits or q_digits in esc_digits:
                    return True
            return False

        records = [r for r in records if _matches(r)]

    paginated = records[offset : offset + limit]
    return [r.model_dump() for r in paginated]


@app.get("/api/calls/{call_id}", response_model=Dict[str, Any])
def get_call_by_id(call_id: str):
    """Retrieves single call record including full conversational transcript."""
    if not state.call_results:
        state.load_initial_data()
    for r in state.call_results:
        if r.call_id == call_id or r.order_id == call_id:
            return r.model_dump()
    # Check SQLite database directly as fallback
    db_rec = state.db.get_call_by_id(call_id) or state.db.get_call_by_order_id(call_id)
    if db_rec:
        return db_rec.model_dump()
    raise HTTPException(status_code=404, detail=f"Call record '{call_id}' not found")


@app.get("/api/calls/{call_id}/audio")
def get_call_audio(call_id: str):
    """Serves the telephony audio recording for a call."""
    audio_dir = DATA_DIR / "audio"
    wav_path = audio_dir / f"{call_id}.wav"
    mp3_path = audio_dir / f"{call_id}.mp3"
    if wav_path.exists():
        return FileResponse(wav_path, media_type="audio/wav", filename=f"{call_id}.wav")
    if mp3_path.exists():
        return FileResponse(mp3_path, media_type="audio/mpeg", filename=f"{call_id}.mp3")

    call = None
    for r in state.call_results:
        if r.call_id == call_id or r.order_id == call_id:
            call = r
            break
    if not call:
        call = state.db.get_call_by_id(call_id)

    if call:
        from scripts.generate_call_audio import generate_telephony_audio
        generated = generate_telephony_audio(wav_path, duration_sec=call.call_duration_seconds or 109)
        return FileResponse(generated, media_type="audio/wav", filename=f"{call_id}.wav")

    raise HTTPException(status_code=404, detail=f"Audio recording for call '{call_id}' not found")


@app.get("/api/calls/{call_id}/recording")
def get_call_recording(call_id: str):
    """Returns recording status, audio stream URL, and duration for a call."""
    if not state.call_results:
        state.load_initial_data()
    call = None
    for r in state.call_results:
        if r.call_id == call_id or r.order_id == call_id:
            call = r
            break
    if not call:
        call = state.db.get_call_by_id(call_id)
    if not call:
        raise HTTPException(status_code=404, detail=f"Call record '{call_id}' not found")

    return {
        "call_id": call.call_id,
        "order_id": call.order_id,
        "supplier_name": call.supplier_name,
        "call_status": call.call_status,
        "recording_url": call.recording_url or f"/api/calls/{call.call_id}/audio",
        "call_duration_seconds": call.call_duration_seconds,
        "has_recording": bool(call.recording_url) or (DATA_DIR / "audio" / f"{call.call_id}.wav").exists(),
    }


@app.post("/api/calls/trigger")
def trigger_outbound_call(payload: TriggerCallPayload):
    """
    Executes a new outbound supplier verification call via CALL-E SDK or high-fidelity simulation.
    Appends the structured outcome to state and updates reports.
    """
    supp = Supplier(
        id=payload.supplier_id,
        name=payload.supplier_name,
        contact_name=payload.contact_name,
        phone=payload.phone_number,
    )
    po = PurchaseOrder(
        order_id=payload.order_id,
        supplier_id=payload.supplier_id,
        item_description=payload.item_description,
        quantity=payload.quantity,
        unit_cost_usd=payload.unit_cost_usd,
        total_value_usd=payload.total_value_usd,
        committed_delivery_date=payload.committed_delivery_date,
        destination_facility=payload.destination_facility,
    )

    scenario_override = None
    if not payload.live:
        scenario_override = {
            "status": payload.mock_status or "ON_TIME",
            "delay_days": payload.delay_days or 0,
            "delay_category": payload.delay_category or "NONE",
            "reason": payload.delay_reason or "All units confirmed packed and shipped.",
            "expedited_freight_cost": payload.expedited_freight_cost or 0.0,
            "escalation_name": payload.contact_name,
            "escalation_phone": payload.phone_number,
        }

    effective_api_key = (payload.api_key.strip() if payload.api_key else None) or CALLE_API_KEY
    has_valid_api_key = bool(
        effective_api_key
        and effective_api_key not in ("your_calle_api_key_here", "calle_live_your_api_key_here")
    )

    is_live = payload.live
    use_mock = not is_live

    if is_live and not has_valid_api_key:
        if payload.api_key is not None or not ENABLE_MOCK_SIMULATOR:
            raise HTTPException(
                status_code=400,
                detail="Valid CALLE_API_KEY is required for live telephony calls. Please configure CALLE_API_KEY in the server .env environment file.",
            )
        else:
            print("[WARN] Live call requested but no valid CALLE_API_KEY configured. Falling back to offline simulator.")
            use_mock = True

    try:
        client = CalleSupplierAgentClient(api_key=effective_api_key, use_mock=use_mock)
        result = client.execute_call(
            supplier=supp,
            order=po,
            scenario_override=scenario_override,
        )
    except Exception as exc:
        print(f"[SERVER ERROR] Call execution failed: {exc}")
        raise HTTPException(
            status_code=400,
            detail=f"Live CALL-E dispatch failed: {str(exc)}",
        )

    if payload.recording_url:
        result.recording_url = payload.recording_url

    # Prepend new result to state & SQLite DB
    state.call_results.insert(0, result)
    state.db.upsert_call_result(result)
    state.report = state.reporter.generate_batch_report(state.call_results)
    state.reporter.export_csv(state.call_results)
    state.reporter.export_json(state.report)
    state.reporter.export_html(state.report)

    msg = (
        f"Live outbound call successfully dispatched via CALL-E to {supp.name} ({supp.phone})"
        if not use_mock
        else f"Verification call executed via offline simulator for {supp.name} ({po.order_id})"
    )

    return {
        "success": True,
        "message": msg,
        "is_live": not use_mock,
        "telephony_mode": "live_calle" if not use_mock else "offline_simulator",
        "result": result.model_dump(),
    }


@app.post("/api/workflow/trigger-batch")
def trigger_batch_workflow(payload: Optional[TriggerBatchWorkflowPayload] = None):
    """
    Triggers an autonomous batch verification workflow across supplier purchase orders.
    Enables single-click bulk verification from the web dashboard or external webhooks.
    """
    if payload is None:
        payload = TriggerBatchWorkflowPayload()

    dataset_path = state.data_path if state.data_path.exists() else (DATA_DIR / "suppliers.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Filter items by category if provided
    items_to_process = []
    for item in raw_data:
        supp_cat = item.get("supplier", {}).get("category", "")
        if payload.category and payload.category.upper() != "ALL":
            if payload.category.lower() not in supp_cat.lower():
                continue
        items_to_process.append(item)

    limit = payload.max_orders if payload.max_orders and payload.max_orders > 0 else 5
    items_to_process = items_to_process[:limit]

    effective_api_key = (payload.api_key.strip() if payload.api_key else None) or CALLE_API_KEY
    has_valid_api_key = bool(
        effective_api_key
        and effective_api_key not in ("your_calle_api_key_here", "calle_live_your_api_key_here")
    )
    is_live = payload.live
    use_mock = not is_live
    if is_live and not has_valid_api_key:
        if payload.api_key is not None or not ENABLE_MOCK_SIMULATOR:
            raise HTTPException(
                status_code=400,
                detail="Valid CALLE_API_KEY is required for live telephony calls. Please configure CALLE_API_KEY in the server .env environment file.",
            )
        else:
            use_mock = True

    client = CalleSupplierAgentClient(api_key=effective_api_key, use_mock=use_mock)
    new_results = []
    for item in items_to_process:
        supp = Supplier(**item["supplier"])
        order = PurchaseOrder(**item["order"])
        mock_scenario = item.get("mock_scenario", {}) if use_mock else None
        res = client.execute_call(
            supplier=supp,
            order=order,
            scenario_override=mock_scenario,
        )
        new_results.append(res)

    # Prepend new results to state in reverse order so latest is on top
    for res in reversed(new_results):
        state.call_results.insert(0, res)

    # Persist all newly executed calls to SQLite DB
    state.db.upsert_call_results_batch(new_results)

    state.report = state.reporter.generate_batch_report(state.call_results)
    state.reporter.export_csv(state.call_results)
    state.reporter.export_json(state.report)
    state.reporter.export_html(state.report)

    return {
        "success": True,
        "message": f"Autonomous batch workflow executed: {len(new_results)} supplier calls completed.",
        "processed_count": len(new_results),
        "total_calls": len(state.call_results),
        "results": [r.model_dump() for r in new_results],
    }



@app.get("/api/export/csv")
def export_csv_report():
    """Streams the generated CSV procurement report."""
    csv_path = OUTPUT_DIR / "procurement_status_report.csv"
    if not csv_path.exists():
        state.reporter.export_csv(state.call_results)
    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=procurement_status_report.csv"},
    )


@app.get("/api/export/json")
def export_json_report():
    """Streams the generated JSON procurement status report."""
    if not state.report:
        state.load_initial_data()
    return JSONResponse(
        content=state.report.model_dump(),
        headers={"Content-Disposition": "attachment; filename=procurement_status_report.json"},
    )


@app.post("/api/reload")
def reload_dataset(dataset: Optional[str] = None):
    """Reloads and recomputes data from the requested dataset."""
    path = Path(dataset) if dataset else (DATA_DIR / "suppliers_enterprise_50.json")
    state.load_initial_data(dataset_path=path, force_recompute=True)
    return {
        "success": True,
        "message": f"Reloaded {len(state.call_results)} call records from {path.name}",
        "total_orders": state.report.total_orders_checked,
    }


def start_server(host: str = "127.0.0.1", port: int = 8000, dataset_path: Optional[Path] = None):
    """Starts the Uvicorn web server."""
    import uvicorn

    if dataset_path:
        state.load_initial_data(dataset_path=dataset_path, force_recompute=True)
    else:
        state.load_initial_data()

    print("=" * 70)
    print(f"🚀 CALL-E Enterprise Telephony Dashboard & API Server Started")
    print(f"• URL: http://{host}:{port}/")
    print(f"• Loaded: {len(state.call_results)} supplier verification calls")
    print(f"• REST API Docs: http://{host}:{port}/docs")
    print("=" * 70)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CALL-E Supply Chain Dashboard Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--data", type=str, default=str(DATA_DIR / "suppliers_enterprise_50.json"), help="Dataset JSON path")
    args = parser.parse_args()

    start_server(host=args.host, port=args.port, dataset_path=Path(args.data))
