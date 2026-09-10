"""
Configuration and settings module for the CALL-E Supplier Status Agent.
Loads configuration from environment variables with safe fallbacks.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# CALL-E API Credentials
CALLE_API_KEY = os.getenv("CALLE_API_KEY", "")
CALLE_AGENT_ID = os.getenv("CALLE_AGENT_ID", "supplier-status-checker-v1")
CALLE_ENVIRONMENT = os.getenv("CALLE_ENVIRONMENT", "sandbox")

# Telephony Parameters
OUTBOUND_CALLER_ID = os.getenv("CALLE_OUTBOUND_CALLER_ID", "+18005550199")
CALL_TIMEOUT_SECONDS = int(os.getenv("CALLE_CALL_TIMEOUT_SECONDS", "180"))
MAX_RETRIES = int(os.getenv("CALLE_MAX_RETRIES", "2"))

# Simulation / Fallback Mode
# If no API key is provided, the client defaults to deterministic simulation mode
ENABLE_MOCK_SIMULATOR = os.getenv("ENABLE_MOCK_SIMULATOR", "true").lower() in ("true", "1", "yes")

# Procurement Business Rules
DEFAULT_DAILY_DELAY_PENALTY_USD = float(os.getenv("DEFAULT_DAILY_DELAY_PENALTY_USD", "1500.0"))
CRITICAL_DELAY_THRESHOLD_DAYS = int(os.getenv("CRITICAL_DELAY_THRESHOLD_DAYS", "3"))
