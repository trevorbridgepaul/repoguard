"""
Enums for the RepoGuard domain.

Enums define the fixed set of valid values for concepts that have a
bounded, known list of options — like severity levels or scan states.
Using enums instead of raw strings prevents typos and makes the code
self-documenting.
"""

from enum import Enum


class Severity(str, Enum):
    """
    How serious a policy violation is.

    Inheriting from both `str` and `Enum` means each value IS a string
    (e.g. Severity.HIGH == "HIGH" is True). This makes serialization to
    JSON trivial — you don't need a custom encoder.

    Ordered from least to most severe so callers can compare:
        Severity.LOW < Severity.CRITICAL  →  True
    That ordering is defined by the integer values below.
    """

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    # Allow comparison by severity level (LOW < MEDIUM < HIGH < CRITICAL).
    # Without this, Python enums are not ordered by default.
    def __lt__(self, other: "Severity") -> bool:
        order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return order.index(self) < order.index(other)


class ScanStatus(str, Enum):
    """
    The lifecycle state of a scan job.

    A scan moves forward through these states in order:
        PENDING → RUNNING → COMPLETE
                          → FAILED  (if something goes wrong)

    Storing status as an enum makes it easy to check what state a scan
    is in without comparing raw strings like "complete" or "done".
    """

    PENDING = "PENDING"    # Scan has been requested but not started yet
    RUNNING = "RUNNING"    # Scan is actively processing files
    COMPLETE = "COMPLETE"  # Scan finished successfully
    FAILED = "FAILED"      # Scan encountered an unrecoverable error
