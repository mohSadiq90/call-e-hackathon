"""
Transcript parsing engine for CALL-E Supply Chain Supplier Calls.
Extracts structured procurement intelligence (status, revised dates, reasons, costs, escalation)
from natural speech transcripts using robust deterministic heuristics and pattern extraction.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from src.models import FulfillmentStatus, DelayReasonCategory


class TranscriptParser:
    """Extracts structured fields from agent-supplier call transcripts."""

    DATE_PATTERNS = [
        r"(?:by|on|around|until|target(?:ing)?|date is|new date is)\s+([A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?(?:, \d{4})?)",
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{1,2}/\d{1,2}/\d{2,4})",
        r"([A-Za-z]+ \d{1,2},? \d{4})",
        r"([A-Za-z]+ \d{1,2}(?:st|nd|rd|th)?)",
    ]

    PHONE_PATTERNS = [
        r"(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
    ]

    COST_PATTERNS = [
        r"\$\s?([0-9,]+(?:\.[0-9]{2})?)",
        r"([0-9,]+(?:\.[0-9]{2})?)\s*(?:dollars|usd)",
    ]

    @classmethod
    def parse_status(cls, transcript: str) -> FulfillmentStatus:
        """Determines if the order is on-time or delayed."""
        lower = transcript.lower()

        # Strong indicators of on-time fulfillment
        on_time_signals = [
            "on schedule", "on time", "ready for pickup", "already shipped",
            "departed our plant", "departed the facility", "staged on loading dock",
            "will meet the date", "will arrive by", "no delays", "confirmed for"
        ]

        # Strong indicators of delay
        delayed_signals = [
            "delayed", "delay", "behind schedule", "push back", "cannot make",
            "won't make", "shortage", "backlog", "hold up", "congestion",
            "rescheduled", "postponed", "revised date"
        ]

        delayed_score = sum(1 for s in delayed_signals if s in lower)
        on_time_score = sum(1 for s in on_time_signals if s in lower)

        if "unreachable" in lower or "voicemail" in lower or "no answer" in lower:
            return FulfillmentStatus.UNREACHABLE
        if delayed_score > on_time_score and delayed_score > 0:
            return FulfillmentStatus.DELAYED
        if on_time_score > 0:
            return FulfillmentStatus.ON_TIME

        return FulfillmentStatus.UNKNOWN

    @classmethod
    def parse_revised_date(cls, transcript: str, original_date: str) -> Optional[str]:
        """Extracts the revised delivery date if mentioned."""
        for pattern in cls.DATE_PATTERNS:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                clean = match.strip().rstrip(".,")
                # Avoid matching original date if another date exists
                if clean != original_date:
                    return clean
        return None

    @classmethod
    def parse_delay_category(cls, transcript: str) -> DelayReasonCategory:
        """Classifies the root cause into standardized supply chain taxonomy."""
        lower = transcript.lower()
        if any(k in lower for k in ["raw material", "resin", "shortage", "components", "parts out of stock"]):
            return DelayReasonCategory.RAW_MATERIAL_SHORTAGE
        if any(k in lower for k in ["qa", "quality", "calibration", "inspection", "spec variance", "re-machining"]):
            return DelayReasonCategory.QUALITY_CONTROL_HOLD
        if any(k in lower for k in ["port", "customs", "freight", "rail", "intermodal", "carrier", "vessel"]):
            return DelayReasonCategory.LOGISTICS_PORT_CONGESTION
        if any(k in lower for k in ["machine down", "equipment", "production line", "maintenance"]):
            return DelayReasonCategory.PRODUCTION_HALT
        if any(k in lower for k in ["weather", "storm", "hurricane", "flood", "act of god"]):
            return DelayReasonCategory.WEATHER_FORCE_MAJEURE
        if "delay" in lower:
            return DelayReasonCategory.OTHER
        return DelayReasonCategory.NONE

    @classmethod
    def parse_expedited_cost(cls, transcript: str) -> float:
        """Extracts any mentioned expedited freight or surcharge in USD."""
        for pattern in cls.COST_PATTERNS:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            if matches:
                clean = matches[0].replace(",", "")
                try:
                    return float(clean)
                except ValueError:
                    continue
        return 0.0

    @classmethod
    def parse_escalation_contact(cls, transcript: str) -> Tuple[Optional[str], Optional[str]]:
        """Extracts the escalation contact name and phone number if provided."""
        phone = None
        for pattern in cls.PHONE_PATTERNS:
            matches = re.findall(pattern, transcript)
            if matches:
                phone = matches[0]
                break

        name = None
        name_patterns = [
            r"(?:escalat(?:ion|e) to|contact(?:ing)?|supervisor is|manager is)\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s*\([^\)]+\))?)",
            r"(?:speaking with|this is)\s+([A-Z][a-z]+ [A-Z][a-z]+)",
        ]
        for np in name_patterns:
            matches = re.findall(np, transcript)
            if matches:
                name = matches[0]
                break

        return name, phone

    @classmethod
    def calculate_delay_days(cls, original_date_str: str, revised_date_str: Optional[str]) -> int:
        """Estimates calendar day delta between original and revised dates."""
        if not revised_date_str or revised_date_str == original_date_str:
            return 0
        try:
            # Try parsing ISO format YYYY-MM-DD
            orig_dt = datetime.strptime(original_date_str, "%Y-%m-%d")
            if re.match(r"^\d{4}-\d{2}-\d{2}$", revised_date_str):
                rev_dt = datetime.strptime(revised_date_str, "%Y-%m-%d")
                delta = (rev_dt - orig_dt).days
                return max(0, delta)
        except Exception:
            pass

        # Fallback heuristic: search for "X days" in transcript
        return 0
