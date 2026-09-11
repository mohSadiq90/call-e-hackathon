"""
Data models and schemas for the Supply Chain Supplier Status Check Agent.
Defines Purchase Orders, Suppliers, Call Transcripts, and Structured Procurement Summaries.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timezone
from pydantic import BaseModel, Field


class FulfillmentStatus(str, Enum):
    ON_TIME = "ON_TIME"
    DELAYED = "DELAYED"
    PARTIAL_DISPATCH = "PARTIAL_DISPATCH"
    UNREACHABLE = "UNREACHABLE"
    UNKNOWN = "UNKNOWN"


class DelayReasonCategory(str, Enum):
    RAW_MATERIAL_SHORTAGE = "RAW_MATERIAL_SHORTAGE"
    PRODUCTION_HALT = "PRODUCTION_HALT"
    LOGISTICS_PORT_CONGESTION = "LOGISTICS_PORT_CONGESTION"
    QUALITY_CONTROL_HOLD = "QUALITY_CONTROL_HOLD"
    WEATHER_FORCE_MAJEURE = "WEATHER_FORCE_MAJEURE"
    NONE = "NONE"
    OTHER = "OTHER"


class Supplier(BaseModel):
    id: str
    name: str
    contact_name: str
    phone: str
    email: Optional[str] = None
    category: str = "Standard"
    timezone: str = "America/New_York"


class PurchaseOrder(BaseModel):
    order_id: str
    supplier_id: str
    item_description: str
    quantity: int
    unit_cost_usd: float
    total_value_usd: float
    committed_delivery_date: str  # YYYY-MM-DD
    destination_facility: str = "Distribution Center 4 (Bentonville, AR)"


class ConversationTurn(BaseModel):
    speaker: str  # "Agent" or "Supplier"
    text: str
    timestamp_offset_sec: float = 0.0


class CallResult(BaseModel):
    call_id: str
    order_id: str
    supplier_name: str
    contact_name: str
    phone_number: str
    call_status: str  # "COMPLETED", "FAILED", "BUSY"
    fulfillment_status: FulfillmentStatus
    original_delivery_date: str
    revised_delivery_date: Optional[str] = None
    delay_days: int = 0
    delay_category: DelayReasonCategory = DelayReasonCategory.NONE
    delay_notes: Optional[str] = None
    expedited_freight_cost_usd: float = 0.0
    estimated_financial_impact_usd: float = 0.0
    escalation_contact_name: Optional[str] = None
    escalation_contact_phone: Optional[str] = None
    escalation_required: bool = False
    call_duration_seconds: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_transcript: str = ""


class BatchProcurementReport(BaseModel):
    report_id: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_orders_checked: int
    on_time_count: int
    delayed_count: int
    unreachable_count: int
    partial_dispatch_count: int = 0
    on_time_percentage: float
    total_financial_risk_usd: float
    critical_escalations: List[CallResult] = []
    call_records: List[CallResult] = []
