"""
In-memory scan storage.

Holds ScanResults for the lifetime of the process, keyed by scan_id.
This is the MVP storage layer — no database, no persistence across
restarts. The API layer imports `scan_store`, the single shared
instance, so a scan submitted in one request can be polled for in
another.
"""

from typing import Optional

from app.domain.models import ScanResult


class ScanStore:
    def __init__(self) -> None:
        self._scans: dict[str, ScanResult] = {}

    def save(self, result: ScanResult) -> None:
        """Save or overwrite a scan result, keyed by its scan_id."""
        self._scans[result.scan_id] = result

    def get(self, scan_id: str) -> Optional[ScanResult]:
        """Look up a scan result by id. Returns None if not found."""
        return self._scans.get(scan_id)


scan_store = ScanStore()
