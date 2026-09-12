"""
SQLite Persistence Layer for CALL-E Supply Chain Intelligence.
Provides production database management, schema migrations, and high-performance
CRUD operations for suppliers, purchase orders, and structured call outcomes.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from config.settings import DATABASE_PATH
from src.models import (
    Supplier,
    PurchaseOrder,
    CallResult,
    FulfillmentStatus,
    DelayReasonCategory,
)


class ProcurementDatabase:
    """
    SQLite-backed persistence manager for procurement telephony data.
    Ensures thread safety, automatic indexing, and lossless Pydantic round-trips.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else DATABASE_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns an optimized SQLite connection with row factories enabled."""
        conn = sqlite3.connect(str(self.db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db(self):
        """Initializes tables and indexes if they do not already exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Call records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS call_records (
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

            # 2. Suppliers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    category TEXT DEFAULT 'Standard',
                    timezone TEXT DEFAULT 'America/New_York'
                );
            """)

            # 3. Purchase orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    order_id TEXT PRIMARY KEY,
                    supplier_id TEXT NOT NULL,
                    item_description TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_cost_usd REAL NOT NULL,
                    total_value_usd REAL NOT NULL,
                    committed_delivery_date TEXT NOT NULL,
                    destination_facility TEXT NOT NULL,
                    FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
                );
            """)

            # 4. Indexes for query acceleration
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_order_id ON call_records(order_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_status ON call_records(fulfillment_status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_category ON call_records(delay_category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_escalation ON call_records(escalation_required);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_timestamp ON call_records(timestamp DESC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_po_supplier_id ON purchase_orders(supplier_id);")

            conn.commit()

    def get_table_names(self) -> List[str]:
        """Returns names of all non-system tables in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            return [row["name"] for row in cursor.fetchall()]

    def upsert_call_result(self, call: CallResult):
        """Inserts or updates a CallResult record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            data_json = json.dumps(call.model_dump())
            cursor.execute("""
                INSERT INTO call_records (
                    call_id, order_id, supplier_name, contact_name, phone_number,
                    call_status, fulfillment_status, original_delivery_date,
                    revised_delivery_date, delay_days, delay_category, delay_notes,
                    expedited_freight_cost_usd, estimated_financial_impact_usd,
                    escalation_contact_name, escalation_contact_phone, escalation_required,
                    call_duration_seconds, timestamp, raw_transcript, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(call_id) DO UPDATE SET
                    order_id = excluded.order_id,
                    supplier_name = excluded.supplier_name,
                    contact_name = excluded.contact_name,
                    phone_number = excluded.phone_number,
                    call_status = excluded.call_status,
                    fulfillment_status = excluded.fulfillment_status,
                    original_delivery_date = excluded.original_delivery_date,
                    revised_delivery_date = excluded.revised_delivery_date,
                    delay_days = excluded.delay_days,
                    delay_category = excluded.delay_category,
                    delay_notes = excluded.delay_notes,
                    expedited_freight_cost_usd = excluded.expedited_freight_cost_usd,
                    estimated_financial_impact_usd = excluded.estimated_financial_impact_usd,
                    escalation_contact_name = excluded.escalation_contact_name,
                    escalation_contact_phone = excluded.escalation_contact_phone,
                    escalation_required = excluded.escalation_required,
                    call_duration_seconds = excluded.call_duration_seconds,
                    timestamp = excluded.timestamp,
                    raw_transcript = excluded.raw_transcript,
                    data_json = excluded.data_json;
            """, (
                call.call_id,
                call.order_id,
                call.supplier_name,
                call.contact_name,
                call.phone_number,
                call.call_status,
                call.fulfillment_status.value,
                call.original_delivery_date,
                call.revised_delivery_date,
                call.delay_days,
                call.delay_category.value,
                call.delay_notes,
                call.expedited_freight_cost_usd,
                call.estimated_financial_impact_usd,
                call.escalation_contact_name,
                call.escalation_contact_phone,
                1 if call.escalation_required else 0,
                call.call_duration_seconds,
                call.timestamp,
                call.raw_transcript,
                data_json,
            ))
            conn.commit()

    def upsert_call_results_batch(self, calls: List[CallResult]) -> int:
        """Batch upserts multiple call results within a single transaction."""
        if not calls:
            return 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            rows = []
            for call in calls:
                data_json = json.dumps(call.model_dump())
                rows.append((
                    call.call_id,
                    call.order_id,
                    call.supplier_name,
                    call.contact_name,
                    call.phone_number,
                    call.call_status,
                    call.fulfillment_status.value,
                    call.original_delivery_date,
                    call.revised_delivery_date,
                    call.delay_days,
                    call.delay_category.value,
                    call.delay_notes,
                    call.expedited_freight_cost_usd,
                    call.estimated_financial_impact_usd,
                    call.escalation_contact_name,
                    call.escalation_contact_phone,
                    1 if call.escalation_required else 0,
                    call.call_duration_seconds,
                    call.timestamp,
                    call.raw_transcript,
                    data_json,
                ))

            cursor.executemany("""
                INSERT INTO call_records (
                    call_id, order_id, supplier_name, contact_name, phone_number,
                    call_status, fulfillment_status, original_delivery_date,
                    revised_delivery_date, delay_days, delay_category, delay_notes,
                    expedited_freight_cost_usd, estimated_financial_impact_usd,
                    escalation_contact_name, escalation_contact_phone, escalation_required,
                    call_duration_seconds, timestamp, raw_transcript, data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(call_id) DO UPDATE SET
                    order_id = excluded.order_id,
                    supplier_name = excluded.supplier_name,
                    contact_name = excluded.contact_name,
                    phone_number = excluded.phone_number,
                    call_status = excluded.call_status,
                    fulfillment_status = excluded.fulfillment_status,
                    original_delivery_date = excluded.original_delivery_date,
                    revised_delivery_date = excluded.revised_delivery_date,
                    delay_days = excluded.delay_days,
                    delay_category = excluded.delay_category,
                    delay_notes = excluded.delay_notes,
                    expedited_freight_cost_usd = excluded.expedited_freight_cost_usd,
                    estimated_financial_impact_usd = excluded.estimated_financial_impact_usd,
                    escalation_contact_name = excluded.escalation_contact_name,
                    escalation_contact_phone = excluded.escalation_contact_phone,
                    escalation_required = excluded.escalation_required,
                    call_duration_seconds = excluded.call_duration_seconds,
                    timestamp = excluded.timestamp,
                    raw_transcript = excluded.raw_transcript,
                    data_json = excluded.data_json;
            """, rows)
            conn.commit()
            return len(rows)

    def _row_to_call_result(self, row: sqlite3.Row) -> CallResult:
        """Converts an SQLite row to a CallResult Pydantic model with data_json fidelity."""
        try:
            raw_dict = json.loads(row["data_json"])
            return CallResult(**raw_dict)
        except Exception:
            return CallResult(
                call_id=row["call_id"],
                order_id=row["order_id"],
                supplier_name=row["supplier_name"],
                contact_name=row["contact_name"],
                phone_number=row["phone_number"],
                call_status=row["call_status"],
                fulfillment_status=FulfillmentStatus(row["fulfillment_status"]),
                original_delivery_date=row["original_delivery_date"],
                revised_delivery_date=row["revised_delivery_date"],
                delay_days=row["delay_days"],
                delay_category=DelayReasonCategory(row["delay_category"]),
                delay_notes=row["delay_notes"],
                expedited_freight_cost_usd=row["expedited_freight_cost_usd"],
                estimated_financial_impact_usd=row["estimated_financial_impact_usd"],
                escalation_contact_name=row["escalation_contact_name"],
                escalation_contact_phone=row["escalation_contact_phone"],
                escalation_required=bool(row["escalation_required"]),
                call_duration_seconds=row["call_duration_seconds"],
                timestamp=row["timestamp"],
                raw_transcript=row["raw_transcript"],
            )

    def get_call_by_id(self, call_id: str) -> Optional[CallResult]:
        """Retrieves a single call record by call_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM call_records WHERE call_id = ? LIMIT 1;", (call_id,))
            row = cursor.fetchone()
            return self._row_to_call_result(row) if row else None

    def get_call_by_order_id(self, order_id: str) -> Optional[CallResult]:
        """Retrieves a single call record by purchase order ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM call_records WHERE order_id = ? ORDER BY timestamp DESC LIMIT 1;", (order_id,))
            row = cursor.fetchone()
            return self._row_to_call_result(row) if row else None

    def list_calls(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        escalation_only: bool = False,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[CallResult]:
        """Queries call records with dynamic filtering, full-text search, and pagination."""
        query = "SELECT * FROM call_records WHERE 1=1"
        params: List[Any] = []

        if status and status.upper() != "ALL":
            query += " AND UPPER(fulfillment_status) = ?"
            params.append(status.upper())

        if category and category.upper() != "ALL":
            query += " AND UPPER(delay_category) = ?"
            params.append(category.upper())

        if escalation_only:
            query += " AND escalation_required = 1"

        if search:
            query += """ AND (
                LOWER(order_id) LIKE ? OR
                LOWER(supplier_name) LIKE ? OR
                LOWER(contact_name) LIKE ? OR
                LOWER(delay_notes) LIKE ? OR
                LOWER(delay_category) LIKE ?
            )"""
            term = f"%{search.lower()}%"
            params.extend([term, term, term, term, term])

        # Order by newest timestamp first
        query += " ORDER BY timestamp DESC"

        if limit is not None and limit > 0:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [self._row_to_call_result(row) for row in cursor.fetchall()]

    def load_all_calls(self) -> List[CallResult]:
        """Loads all call records ordered chronologically (newest first)."""
        return self.list_calls()

    def count_calls(self) -> int:
        """Returns total count of stored call records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM call_records;")
            return cursor.fetchone()[0]

    def save_supplier(self, supplier: Supplier):
        """Saves or updates a Supplier record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suppliers (id, name, contact_name, phone, email, category, timezone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    contact_name = excluded.contact_name,
                    phone = excluded.phone,
                    email = excluded.email,
                    category = excluded.category,
                    timezone = excluded.timezone;
            """, (
                supplier.id,
                supplier.name,
                supplier.contact_name,
                supplier.phone,
                supplier.email,
                supplier.category,
                supplier.timezone,
            ))
            conn.commit()

    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Retrieves a supplier by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE id = ? LIMIT 1;", (supplier_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Supplier(
                id=row["id"],
                name=row["name"],
                contact_name=row["contact_name"],
                phone=row["phone"],
                email=row["email"],
                category=row["category"],
                timezone=row["timezone"],
            )

    def list_suppliers(self) -> List[Supplier]:
        """Lists all registered suppliers."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers ORDER BY name ASC;")
            return [
                Supplier(
                    id=row["id"],
                    name=row["name"],
                    contact_name=row["contact_name"],
                    phone=row["phone"],
                    email=row["email"],
                    category=row["category"],
                    timezone=row["timezone"],
                )
                for row in cursor.fetchall()
            ]

    def save_purchase_order(self, order: PurchaseOrder):
        """Saves or updates a PurchaseOrder record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO purchase_orders (
                    order_id, supplier_id, item_description, quantity,
                    unit_cost_usd, total_value_usd, committed_delivery_date,
                    destination_facility
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    supplier_id = excluded.supplier_id,
                    item_description = excluded.item_description,
                    quantity = excluded.quantity,
                    unit_cost_usd = excluded.unit_cost_usd,
                    total_value_usd = excluded.total_value_usd,
                    committed_delivery_date = excluded.committed_delivery_date,
                    destination_facility = excluded.destination_facility;
            """, (
                order.order_id,
                order.supplier_id,
                order.item_description,
                order.quantity,
                order.unit_cost_usd,
                order.total_value_usd,
                order.committed_delivery_date,
                order.destination_facility,
            ))
            conn.commit()

    def get_purchase_order(self, order_id: str) -> Optional[PurchaseOrder]:
        """Retrieves a purchase order by order_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM purchase_orders WHERE order_id = ? LIMIT 1;", (order_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return PurchaseOrder(
                order_id=row["order_id"],
                supplier_id=row["supplier_id"],
                item_description=row["item_description"],
                quantity=row["quantity"],
                unit_cost_usd=row["unit_cost_usd"],
                total_value_usd=row["total_value_usd"],
                committed_delivery_date=row["committed_delivery_date"],
                destination_facility=row["destination_facility"],
            )

    def save_suppliers_and_orders(self, dataset: List[Dict[str, Any]]):
        """Seeds suppliers and purchase orders from raw JSON dataset."""
        with self._get_connection() as conn:
            for item in dataset:
                supp_dict = item.get("supplier", {})
                order_dict = item.get("order", {})
                if supp_dict:
                    self.save_supplier(Supplier(**supp_dict))
                if order_dict:
                    self.save_purchase_order(PurchaseOrder(**order_dict))

    def clear_all_calls(self):
        """Deletes all call records."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM call_records;")
            conn.commit()

    def clear_all(self):
        """Clears all tables in the database."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM call_records;")
            conn.execute("DELETE FROM purchase_orders;")
            conn.execute("DELETE FROM suppliers;")
            conn.commit()
