"""
Policy registry.

Central place that knows about every policy in the system. The scanner
and the future `/policies` API endpoint go through this registry instead
of importing individual policy modules directly.
"""

from app.policies.base import Policy
from app.policies.codeowners_exists import CodeownersExistsPolicy
from app.policies.gitignore_exists import GitignoreExistsPolicy
from app.policies.no_secrets import NoSecretsPolicy
from app.policies.readme_exists import ReadmeExistsPolicy

_REGISTRY: dict[str, Policy] = {
    p.policy_id: p
    for p in [
        ReadmeExistsPolicy(),
        GitignoreExistsPolicy(),
        CodeownersExistsPolicy(),
        NoSecretsPolicy(),
    ]
}


def get_policy(policy_id: str) -> Policy:
    """Look up a single policy by its policy_id. Raises KeyError if unknown."""
    return _REGISTRY[policy_id]


def get_all_policies() -> list[Policy]:
    """Return every registered policy."""
    return list(_REGISTRY.values())


def get_policies(policy_ids: list[str] | None) -> list[Policy]:
    """
    Resolve a list of policy_ids to Policy instances.

    None means "run everything" — matches ScanRequest.policies semantics.
    """
    if policy_ids is None:
        return get_all_policies()
    return [_REGISTRY[policy_id] for policy_id in policy_ids]
