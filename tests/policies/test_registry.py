"""
Tests for the policy registry.
"""

import pytest

from app.policies.codeowners_exists import CodeownersExistsPolicy
from app.policies.gitignore_exists import GitignoreExistsPolicy
from app.policies.readme_exists import ReadmeExistsPolicy
from app.policies.registry import get_all_policies, get_policies, get_policy


def test_get_all_policies_returns_every_registered_policy():
    policies = get_all_policies()

    assert len(policies) == 8
    policy_ids = {p.policy_id for p in policies}
    assert policy_ids == {
        "readme_exists",
        "gitignore_exists",
        "codeowners_exists",
        "no_secrets",
        "large_files",
        "no_print_statements",
        "license_header",
        "dependency_pinning",
    }


def test_get_policy_returns_the_matching_instance():
    policy = get_policy("readme_exists")

    assert isinstance(policy, ReadmeExistsPolicy)


def test_get_policy_raises_for_unknown_id():
    with pytest.raises(KeyError):
        get_policy("not_a_real_policy")


def test_get_policies_with_none_returns_everything():
    policies = get_policies(None)

    assert len(policies) == 8


def test_get_policies_with_explicit_list_returns_only_those():
    policies = get_policies(["gitignore_exists", "codeowners_exists"])

    assert len(policies) == 2
    assert {type(p) for p in policies} == {GitignoreExistsPolicy, CodeownersExistsPolicy}


def test_get_policies_raises_for_unknown_id_in_list():
    with pytest.raises(KeyError):
        get_policies(["readme_exists", "not_a_real_policy"])
