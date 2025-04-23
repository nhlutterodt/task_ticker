# debug/logging.py
"""
Central Debug Logger, Decorator, and Trace Function
- Provides timestamped, leveled logs (pretty, JSON, or both)
- @debug_trace decorator for function tracing
- trace() for ad hoc debug messages
"""
import sys
import json
import time
import functools
from datetime import datetime
from .config import DEBUG_ENABLED, LOG_LEVEL, LOG_FORMAT, LOG_FILE

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _should_log(level):
    if not DEBUG_ENABLED:
        return False
    try:
        return LOG_LEVELS.index(level) >= LOG_LEVELS.index(LOG_LEVEL)
    except ValueError:
        return True


def _format_pretty(level, msg, context=None):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ctx = f" [{context}]" if context else ""
    return f"[{ts}][{level}]{ctx} {msg}"


def _format_json(level, msg, context=None, extra=None):
    log = {
        "timestamp": time.time(),
        "level": level,
        "context": context,
        "message": msg,
    }
    if extra:
        log.update(extra)
    return json.dumps(log, ensure_ascii=False)


def _write_log(line):
    if LOG_FILE:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    else:
        print(line, file=sys.stderr)


def trace(msg, level="DEBUG", context=None, extra=None):
    if not _should_log(level):
        return
    if LOG_FORMAT in ("pretty", "both"):
        _write_log(_format_pretty(level, msg, context))
    if LOG_FORMAT in ("json", "both"):
        _write_log(_format_json(level, msg, context, extra))


def debug_trace(func):
    """Decorator to log function entry, exit, args, return, and exceptions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not DEBUG_ENABLED:
            return func(*args, **kwargs)
        fname = func.__name__
        arglist = []
        if args:
            arglist += [repr(a) for a in args]
        if kwargs:
            arglist += [f"{k}={v!r}" for k, v in kwargs.items()]
        trace(f"{fname} called with {', '.join(arglist)}", context=fname)
        try:
            result = func(*args, **kwargs)
            trace(f"{fname} returned {repr(result)}", context=fname)
            return result
        except Exception as e:
            trace(f"{fname} raised {e.__class__.__name__}: {e}", level="ERROR", context=fname)
            raise
    return wrapper
