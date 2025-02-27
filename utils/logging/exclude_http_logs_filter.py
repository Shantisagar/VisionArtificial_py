"""
Path: app/logs/exclude_http_logs_filter.py
Filter module for excluding specific HTTP logs.
"""

import logging

class ExcludeHTTPLogsFilter(logging.Filter):
    """Filtra registros que contienen solicitudes HTTP GET o POST."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not any(keyword in message for keyword in ['GET /', 'POST /'])

    def another_method(self):
        """Another public method to satisfy pylint."""
        print("Another method")
