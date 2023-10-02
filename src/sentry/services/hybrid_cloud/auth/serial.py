from __future__ import annotations

from sentry.models import (
    ApiKey,
    AuthIdentity,
    AuthIdentityReplica,
    AuthProvider,
    AuthProviderReplica,
)
from sentry.services.hybrid_cloud.auth import (
    RpcApiKey,
    RpcAuthIdentity,
    RpcAuthProvider,
    RpcAuthProviderFlags,
)


def _serialize_auth_provider_flags(ap: AuthProvider) -> RpcAuthProviderFlags:
    return RpcAuthProviderFlags.serialize_by_field_name(ap.flags, value_transform=bool)


def serialize_auth_provider(ap: AuthProvider) -> RpcAuthProvider:
    return RpcAuthProvider(
        id=ap.id,
        organization_id=ap.organization_id,
        provider=ap.provider,
        flags=_serialize_auth_provider_flags(ap),
        config=ap.config,
        default_role=ap.default_role,
        default_global_access=ap.default_global_access,
    )


def serialize_auth_provider_replica(ap: AuthProviderReplica) -> RpcAuthProvider:
    return RpcAuthProvider(
        id=ap.auth_provider_id,
        provider=ap.provider,
        flags=RpcAuthProviderFlags(
            allow_unlinked=ap.allow_unlinked,
            scim_enabled=ap.scim_enabled,
        ),
        config=ap.config,
        default_role=ap.default_role,
        default_global_access=ap.default_global_access,
    )


def serialize_auth_identity(ai: AuthIdentity) -> RpcAuthIdentity:
    return RpcAuthIdentity(
        id=ai.id,
        user_id=ai.user_id,
        auth_provider_id=ai.auth_provider_id,
        ident=ai.ident,
        data=ai.data,
        last_verified=ai.last_verified,
    )


def serialize_auth_identity_replica(ai: AuthIdentityReplica) -> RpcAuthIdentity:
    return RpcAuthIdentity(
        id=ai.auth_identity_id,
        user_id=ai.user_id,
        auth_provider_id=ai.auth_provider_id,
        ident=ai.ident,
        data=ai.data,
        last_verified=ai.last_verified,
    )


def serialize_api_key(ak: ApiKey) -> RpcApiKey:
    return RpcApiKey(
        id=ak.id,
        organization_id=ak.organization_id,
        key=ak.key,
        status=ak.status,
        allowed_origins=ak.get_allowed_origins(),
        label=ak.label,
        scope_list=ak.get_scopes(),
    )
