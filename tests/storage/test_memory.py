"""
Tests for the in-memory ScanStore.
"""

from app.domain.models import ScanResult
from app.storage.memory import ScanStore


def test_save_then_get_returns_the_same_result():
    store = ScanStore()
    result = ScanResult(repo_path="/tmp/repo")

    store.save(result)

    assert store.get(result.scan_id) is result


def test_get_returns_none_for_unknown_scan_id():
    store = ScanStore()

    assert store.get("not-a-real-scan-id") is None


def test_save_overwrites_existing_result_with_same_scan_id():
    store = ScanStore()
    original = ScanResult(repo_path="/tmp/repo")
    store.save(original)

    updated = ScanResult(repo_path="/tmp/repo", scan_id=original.scan_id)
    store.save(updated)

    assert store.get(original.scan_id) is updated


def test_separate_instances_do_not_share_state():
    store_a = ScanStore()
    store_b = ScanStore()
    result = ScanResult(repo_path="/tmp/repo")

    store_a.save(result)

    assert store_b.get(result.scan_id) is None
