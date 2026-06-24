"""
Tests for Policy.info(), exercised against the real registered policies.
"""

from app.domain.enums import Severity
from app.domain.models import PolicyInfo
from app.policies.registry import get_all_policies


def test_every_registered_policy_returns_a_policy_info():
    for policy in get_all_policies():
        info = policy.info()

        assert isinstance(info, PolicyInfo)
        assert info.policy_id == policy.policy_id
        assert info.name
        assert info.description
        assert isinstance(info.severity, Severity)
