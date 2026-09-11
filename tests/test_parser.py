"""Tests for TranscriptParser in src.transcript_parser."""

import unittest
from src.models import FulfillmentStatus, DelayReasonCategory
from src.transcript_parser import TranscriptParser


class TestTranscriptParser(unittest.TestCase):

    def test_parse_status_on_time(self):
        transcript = (
            "Agent: Is this order on schedule?\n"
            "Supplier: Yes, absolutely! Everything is on schedule to arrive by September 18."
        )
        status = TranscriptParser.parse_status(transcript)
        self.assertEqual(status, FulfillmentStatus.ON_TIME)

    def test_parse_status_delayed(self):
        transcript = (
            "Agent: Is this shipment on schedule?\n"
            "Supplier: Unfortunately we are behind schedule due to port congestion."
        )
        status = TranscriptParser.parse_status(transcript)
        self.assertEqual(status, FulfillmentStatus.DELAYED)

    def test_parse_status_partial_dispatch(self):
        transcript = (
            "Agent: What is the status of PO-91009?\n"
            "Supplier: We have a partial dispatch situation. 1,400 units are en route."
        )
        status = TranscriptParser.parse_status(transcript)
        self.assertEqual(status, FulfillmentStatus.PARTIAL_DISPATCH)

    def test_parse_status_unreachable(self):
        transcript = (
            "Agent: Urgent status verification on PO-91015.\n"
            "Automated System: The party you are trying to reach is currently unavailable. Please leave a voicemail."
        )
        status = TranscriptParser.parse_status(transcript)
        self.assertEqual(status, FulfillmentStatus.UNREACHABLE)

    def test_parse_revised_date(self):
        transcript = "Our revised date is September 22. We guarantee delivery on September 22."
        revised = TranscriptParser.parse_revised_date(transcript, "September 15")
        self.assertIsNotNone(revised)
        self.assertIn("September 22", revised)

    def test_parse_delay_category(self):
        t1 = "We experienced a raw material shortage with resin."
        self.assertEqual(TranscriptParser.parse_delay_category(t1), DelayReasonCategory.RAW_MATERIAL_SHORTAGE)

        t2 = "Calibration inspection failed in quality control."
        self.assertEqual(TranscriptParser.parse_delay_category(t2), DelayReasonCategory.QUALITY_CONTROL_HOLD)

        t3 = "The vessel was held up by container port congestion."
        self.assertEqual(TranscriptParser.parse_delay_category(t3), DelayReasonCategory.LOGISTICS_PORT_CONGESTION)

    def test_parse_cost(self):
        transcript = "The expedited courier run will add $1,250.00 to the freight bill."
        cost = TranscriptParser.parse_expedited_cost(transcript)
        self.assertEqual(cost, 1250.0)

    def test_calculate_delay_days(self):
        delta = TranscriptParser.calculate_delay_days("2026-09-15", "2026-09-20")
        self.assertEqual(delta, 5)


if __name__ == "__main__":
    unittest.main()
