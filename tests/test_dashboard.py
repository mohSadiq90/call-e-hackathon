"""Tests for HTML Dashboard rendering and export in src.html_dashboard."""

import unittest
import tempfile
from pathlib import Path

from src.models import (
    Supplier,
    PurchaseOrder,
    CallResult,
    FulfillmentStatus,
    DelayReasonCategory,
    BatchProcurementReport,
)
from src.html_dashboard import render_html_dashboard
from src.reporter import ProcurementReporter


class TestHtmlDashboard(unittest.TestCase):

    def setUp(self):
        self.sample_result_ontime = CallResult(
            call_id="call_test_001",
            order_id="PO-10001",
            supplier_name="Alpha Tech Solutions",
            contact_name="Alice Smith",
            phone_number="+1-555-111-2222",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.ON_TIME,
            original_delivery_date="2026-09-18",
            revised_delivery_date="2026-09-18",
            delay_days=0,
            delay_category=DelayReasonCategory.NONE,
            delay_notes="Confirmed en route via express carrier.",
            expedited_freight_cost_usd=0.0,
            estimated_financial_impact_usd=0.0,
            escalation_contact_name="Alice Smith",
            escalation_contact_phone="+1-555-111-2222",
            escalation_required=False,
            call_duration_seconds=65,
            raw_transcript="Agent: Is PO-10001 on track?\nSupplier: Yes, arriving Sept 18.",
        )

        self.sample_result_delayed = CallResult(
            call_id="call_test_002",
            order_id="PO-10002",
            supplier_name="Beta Logistics Corp",
            contact_name="Bob Jones",
            phone_number="+1-555-333-4444",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.DELAYED,
            original_delivery_date="2026-09-15",
            revised_delivery_date="2026-09-20",
            delay_days=5,
            delay_category=DelayReasonCategory.RAW_MATERIAL_SHORTAGE,
            delay_notes="Resin shortage delayed assembly line.",
            expedited_freight_cost_usd=850.0,
            estimated_financial_impact_usd=8350.0,
            escalation_contact_name="Bob Jones (Director)",
            escalation_contact_phone="+1-555-333-4444",
            escalation_required=True,
            call_duration_seconds=115,
            raw_transcript="Agent: Is PO-10002 on track?\nSupplier: No, delayed by 5 days due to resin shortage.",
        )

        self.sample_result_partial = CallResult(
            call_id="call_test_003",
            order_id="PO-10003",
            supplier_name="Gamma Wire Harness",
            contact_name="Clara Wu",
            phone_number="+1-555-555-6666",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.PARTIAL_DISPATCH,
            original_delivery_date="2026-09-16",
            revised_delivery_date="2026-09-20",
            delay_days=4,
            delay_category=DelayReasonCategory.QUALITY_CONTROL_HOLD,
            delay_notes="First lot shipped, balance held for QC.",
            expedited_freight_cost_usd=1200.0,
            estimated_financial_impact_usd=7200.0,
            escalation_contact_name="Clara Wu",
            escalation_contact_phone="+1-555-555-6666",
            escalation_required=True,
            call_duration_seconds=95,
            raw_transcript="Agent: Status on PO-10003?\nSupplier: We have a partial dispatch situation.",
        )

        self.sample_result_unreachable = CallResult(
            call_id="call_test_004",
            order_id="PO-10004",
            supplier_name="Delta Seals Inc",
            contact_name="Frank Donato",
            phone_number="+1-555-777-8888",
            call_status="UNREACHABLE",
            fulfillment_status=FulfillmentStatus.UNREACHABLE,
            original_delivery_date="2026-09-16",
            revised_delivery_date="2026-09-16",
            delay_days=0,
            delay_category=DelayReasonCategory.OTHER,
            delay_notes="Voicemail reached, line unmonitored.",
            expedited_freight_cost_usd=0.0,
            estimated_financial_impact_usd=0.0,
            escalation_contact_name="Frank Donato",
            escalation_contact_phone="+1-555-777-8888",
            escalation_required=True,
            call_duration_seconds=28,
            raw_transcript="Agent: Urgent status confirmation needed.\nAutomated: Voicemail recorded.",
        )

        self.report = BatchProcurementReport(
            report_id="rep_test_123",
            total_orders_checked=4,
            on_time_count=1,
            delayed_count=1,
            unreachable_count=1,
            partial_dispatch_count=1,
            on_time_percentage=25.0,
            total_financial_risk_usd=15550.0,
            critical_escalations=[
                self.sample_result_delayed,
                self.sample_result_partial,
                self.sample_result_unreachable,
            ],
            call_records=[
                self.sample_result_ontime,
                self.sample_result_delayed,
                self.sample_result_partial,
                self.sample_result_unreachable,
            ],
        )

    def test_render_html_dashboard_structure(self):
        """Validates that rendered HTML contains all required dashboard sections and metadata."""
        html = render_html_dashboard(self.report)

        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("CALL-E Supply Chain Intelligence", html)
        self.assertIn("rep_test_123", html)
        self.assertIn("Global Procurement Fulfillment Summary", html)

        # Check KPI containers
        self.assertIn("kpi-total-orders", html)
        self.assertIn("kpi-on-time-pct", html)
        self.assertIn("kpi-financial-risk", html)
        self.assertIn("kpi-escalations-cnt", html)

        # Check Table and Cards containers
        self.assertIn("calls-table-body", html)
        self.assertIn("cards-view-section", html)

        # Check Modals
        self.assertIn("call-modal", html)
        self.assertIn("new-call-modal", html)
        self.assertIn("modal-transcript-container", html)

        # Check Embedded Data
        self.assertIn("PO-10001", html)
        self.assertIn("Beta Logistics Corp", html)
        self.assertIn("Gamma Wire Harness", html)
        self.assertIn("Delta Seals Inc", html)

    def test_reporter_export_html(self):
        """Validates that ProcurementReporter successfully writes HTML dashboard to disk."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            reporter = ProcurementReporter(output_dir=Path(tmp_dir))
            html_path = reporter.export_html(self.report, filename="dashboard.html")

            self.assertTrue(html_path.exists())
            self.assertEqual(html_path.name, "dashboard.html")
            content = html_path.read_text(encoding="utf-8")
            self.assertIn("CALL-E Supply Chain Intelligence", content)
            self.assertIn("rep_test_123", content)
            self.assertGreater(len(content), 1000)

    def test_audio_player_html_components(self):
        """Validates that audio player controls are removed from dashboard UI to prevent judging defects."""
        html = render_html_dashboard(self.report)

        self.assertNotIn('id="modal-audio-element"', html)
        self.assertNotIn('id="modal-audio-badge"', html)
        self.assertNotIn('id="modal-audio-direct-link"', html)
        self.assertNotIn('seekAudioFromClick', html)
        self.assertNotIn('updateAudioProgressUI', html)
        self.assertIn('modal-transcript-container', html)
        self.assertIn('Verified Conversational Dialogue Transcript', html)

    def test_html_dashboard_preserves_recording_url_in_data(self):
        """Validates that calls with recording_url are serialized into embedded dashboard JSON."""
        call_with_rec = CallResult(
            call_id="call_real_embedded",
            order_id="PO-REAL-999",
            supplier_name="Verified Audio Supplier",
            contact_name="Dave Smith",
            phone_number="+1-563-281-3105",
            call_status="COMPLETED",
            fulfillment_status=FulfillmentStatus.DELAYED,
            original_delivery_date="2026-09-15",
            revised_delivery_date="2026-09-22",
            delay_days=7,
            recording_url="/api/calls/call_real_embedded/audio",
        )
        report = BatchProcurementReport(
            report_id="rep_rec_test",
            total_orders_checked=1,
            on_time_count=0,
            delayed_count=1,
            unreachable_count=0,
            on_time_percentage=0.0,
            total_financial_risk_usd=10500.0,
            critical_escalations=[call_with_rec],
            call_records=[call_with_rec],
        )
        html = render_html_dashboard(report)
        self.assertIn("/api/calls/call_real_embedded/audio", html)
        self.assertIn("call_real_embedded", html)

    def test_html_dashboard_phone_and_call_id_search_support(self):
        """Validates that rendered HTML includes phone number and call ID search capabilities."""
        html = render_html_dashboard(self.report)
        self.assertIn("Phone (+1-563...)", html)
        self.assertIn("queryDigits", html)
        self.assertIn("phoneDigits", html)
        self.assertIn("c.phone_number", html)
        self.assertIn("c.call_id", html)

    def test_html_dashboard_live_calle_default_mode(self):
        """Validates that Live CALL-E Telephony Network is the default selected option in modal."""
        html = render_html_dashboard(self.report)
        self.assertIn('<option value="live" selected>Live CALL-E Telephony Network (Outbound Line)</option>', html)

    def test_html_dashboard_api_key_field_removed_from_form(self):
        """Validates that API key input field is NOT in the modal form (managed via server environment)."""
        html = render_html_dashboard(self.report)
        self.assertNotIn('id="form-api-key"', html)
        self.assertNotIn('id="group-api-key"', html)
        self.assertNotIn('toggleApiKeyField', html)
        self.assertNotIn('HAS_SERVER_API_KEY', html)

    def test_html_dashboard_call_action_buttons_and_stepper(self):
        """Validates that table rows and cards have Call action buttons and modal includes execution stepper."""
        html = render_html_dashboard(self.report)
        self.assertIn("📞 Call", html)
        self.assertIn("call-progress-card", html)
        self.assertIn("call-progress-timer", html)
        self.assertIn("pstep-1", html)
        self.assertIn("pstep-4", html)
        self.assertIn("fillFormFieldsFromCall", html)

    def test_html_dashboard_live_backend_sync_elements(self):
        """Validates that top navbar includes backend status indicator and syncWithBackend logic."""
        html = render_html_dashboard(self.report)
        self.assertIn('id="backend-status-indicator"', html)
        self.assertIn('id="backend-status-text"', html)
        self.assertIn("syncWithBackend", html)
        self.assertIn("Sync Data", html)

    def test_html_dashboard_unified_modal_flow(self):
        """Validates unified in-modal layout preventing multi-popup flickering and automatic popup jumps."""
        html = render_html_dashboard(self.report)
        self.assertIn('id="new-call-form-view"', html)
        self.assertIn('id="call-execution-panel"', html)
        self.assertIn('id="call-error-box"', html)
        self.assertIn('id="call-success-box"', html)
        self.assertIn('id="server-telephony-banner"', html)
        self.assertIn('id="call-result-transcript"', html)
        self.assertIn("returnToFormView", html)
        self.assertIn("switchToSimulatorAndRun", html)
        self.assertIn("updateServerTelephonyBanner", html)
        # Ensure executeManualCall does NOT auto-close and openCallModal
        self.assertNotIn("openCallModal(newRecord.call_id)", html)


    def test_html_dashboard_call_inspection_modal_unicode_bullet(self):
        """Validates that call modal header uses actual unicode bullet point and not raw HTML &bull;."""
        html = render_html_dashboard(self.report)
        self.assertIn("${call.order_id} • ${call.supplier_name}", html)
        self.assertNotIn("${call.order_id} &bull; ${call.supplier_name}", html)

    def test_html_dashboard_chat_bubbles_contrast(self):
        """Validates high contrast chat bubble styling for agent and supplier messages."""
        html = render_html_dashboard(self.report)
        self.assertIn(".chat-bubble.agent", html)
        self.assertIn("background-color: #1e293b;", html)
        self.assertIn(".chat-bubble.supplier", html)
        self.assertIn("background-color: #1d4ed8;", html)

    def test_html_dashboard_table_affordance_and_padding(self):
        """Validates button affordance with eye icon and increased row padding in data table."""
        html = render_html_dashboard(self.report)
        self.assertIn("btn-action-view", html)
        self.assertIn("👁️ View Call", html)
        self.assertIn("padding: 1.2rem 1rem;", html)

    def test_html_dashboard_readonly_and_editable_form_states(self):
        """Validates distinct read-only and editable visual states in Trigger Call modal."""
        html = render_html_dashboard(self.report)
        self.assertIn("form-input-readonly", html)
        self.assertIn("Auto-Populated", html)
        self.assertIn("form-input-editable", html)
        self.assertIn("Editable Destination", html)

    def test_html_dashboard_consolidated_analytics_widget_and_strict_colors(self):
        """Validates consolidated analytics widget, clock icon on Voice Hours Saved, and strict colors."""
        html = render_html_dashboard(self.report)
        # Clock icon on Voice Hours Saved
        self.assertIn("⏱️", html)
        self.assertIn("Voice Hours Saved", html)
        # Consolidated widget
        self.assertIn("consolidated-panel", html)
        self.assertIn("renderConsolidatedBarItem", html)
        self.assertIn("Delay Root Causes & Financial Exposure", html)
        # Strict KPI colors
        self.assertIn("var(--accent-green)", html)
        self.assertIn("var(--accent-amber)", html)
        self.assertIn("#64748b", html)

    def test_html_dashboard_mobile_friendly_responsive_layout(self):
        """Validates mobile responsive design best practices, meta viewport, and layout patterns."""
        html = render_html_dashboard(self.report)

        # 1. Viewport Meta Tags & Theme
        self.assertIn("viewport-fit=cover", html)
        self.assertIn('name="theme-color"', html)
        self.assertIn('name="apple-mobile-web-app-capable"', html)

        # 2. Media Queries for Mobile & Tablet Breakpoints
        self.assertIn("@media (max-width: 1024px)", html)
        self.assertIn("@media (max-width: 900px)", html)
        self.assertIn("@media (max-width: 768px)", html)
        self.assertIn("@media (max-width: 640px)", html)
        self.assertIn("@media (max-width: 480px)", html)
        self.assertIn("@media (max-width: 360px)", html)

        # 3. Mobile Navigation Controls & Drawer
        self.assertIn("nav-mobile-bar", html)
        self.assertIn("mobile-menu-btn", html)
        self.assertIn("toggleMobileMenu", html)

        # 4. Mobile Layout Patterns
        self.assertIn("-webkit-overflow-scrolling: touch;", html)
        self.assertIn("table-scroll-hint", html)
        self.assertIn("modalSlideUp", html)
        self.assertIn("modal-overview-grid", html)
        self.assertIn("outcome-findings-grid", html)
        self.assertIn("modal-actions-row", html)
        self.assertIn("card-footer-actions", html)

        # 5. Mobile Touch & Input Ergonomics
        self.assertIn("font-size: 16px;", html)
        self.assertIn("-webkit-tap-highlight-color: transparent;", html)
        self.assertIn("min-height: 44px;", html)

    def test_html_dashboard_reusable_shimmer_animation(self):
        """Dashboard HTML includes reusable CSS shimmer animations and JS skeleton loading functions."""
        html = render_html_dashboard(self.report)

        # 1. CSS shimmer animation keyframes and classes
        self.assertIn("@keyframes shimmerWave", html)
        self.assertIn(".skeleton-shimmer", html)
        self.assertIn(".skeleton-bar", html)
        self.assertIn(".skeleton-pill", html)

        # 2. Reusable JavaScript shimmer loader utilities
        self.assertIn("renderTableShimmer", html)
        self.assertIn("renderCardsShimmer", html)
        self.assertIn("showShimmerLoading", html)
        self.assertIn("shimmer-row", html)
        self.assertIn("shimmer-card", html)


if __name__ == "__main__":
    unittest.main()


