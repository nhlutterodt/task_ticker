# debug/config.py
"""
Debug Framework Configuration
Controls toggles for debug mode, log level, and output format (pretty, json, or both).
"""
import os

# Debug enabled flag (env var: DEBUG, default: False)
DEBUG_ENABLED = os.getenv("DEBUG", "0").lower() in ("1", "true", "yes", "on")

# Log level (env var: DEBUG_LEVEL, default: "DEBUG")
LOG_LEVEL = os.getenv("DEBUG_LEVEL", "DEBUG").upper()

# Log output format: "pretty", "json", or "both" (env var: DEBUG_FORMAT)
LOG_FORMAT = os.getenv("DEBUG_FORMAT", "pretty").lower()

# Log file path (env var: DEBUG_LOGFILE, default: None)
LOG_FILE = os.getenv("DEBUG_LOGFILE") or None
