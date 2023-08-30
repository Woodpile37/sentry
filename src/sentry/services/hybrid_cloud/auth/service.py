# Please do not use
#     from __future__ import annotations
# in modules such as this one where hybrid cloud data models or service classes are
# defined, because we want to reflect on type annotations and avoid forward references.

import abc
from typing import Any, List, Mapping, Optional, cast

from sentry.services.hybrid_cloud.auth import (
    AuthenticationContext,
    AuthenticationRequest,
    MiddlewareAuthenticationResponse,
    RpcAuthenticatorType,
    RpcAuthProvider,
    RpcAuthState,
    RpcOrganizationAuthConfig,
)
from sentry.services.hybrid_cloud.organization import RpcOrganizationMemberSummary
from sentry.services.hybrid_cloud.rpc import RpcService, rpc_method
from sentry.silo import SiloMode


class AuthService(RpcService):
    key = "auth"
    local_mode = SiloMode.CONTROL

    @classmethod
    def get_local_implementation(cls) -> RpcService:
        from sentry.services.hybrid_cloud.auth.impl import DatabaseBackedAuthService

        return DatabaseBackedAuthService()

    @rpc_method
    @abc.abstractmethod
    def authenticate(self, *, request: AuthenticationRequest) -> MiddlewareAuthenticationResponse:
        pass

    @rpc_method
    @abc.abstractmethod
    def authenticate_with(
        self, *, request: AuthenticationRequest, authenticator_types: List[RpcAuthenticatorType]
    ) -> AuthenticationContext:
        pass

    @rpc_method
    @abc.abstractmethod
    def get_org_auth_config(
        self, *, organization_ids: List[int]
    ) -> List[RpcOrganizationAuthConfig]:
        pass

    @rpc_method
    @abc.abstractmethod
    def get_user_auth_state(
        self,
        *,
        user_id: int,
        is_superuser: bool,
        organization_id: Optional[int],
        org_member: Optional[RpcOrganizationMemberSummary],
    ) -> RpcAuthState:
        pass

    # TODO: Denormalize this scim enabled flag onto organizations?
    # This is potentially a large list
    @rpc_method
    @abc.abstractmethod
    def get_org_ids_with_scim(self) -> List[int]:
        """
        This method returns a list of org ids that have scim enabled
        :return:
        """
        pass

    @rpc_method
    @abc.abstractmethod
    def get_auth_providers(self, *, organization_id: int) -> List[RpcAuthProvider]:
        """DEPRECATED. TODO: Delete after usages are removed from getsentry."""

    @rpc_method
    @abc.abstractmethod
    def get_auth_provider(self, *, organization_id: int) -> Optional[RpcAuthProvider]:
        """
        This method returns the auth provider for an org, if one exists
        """
        pass

    @rpc_method
    @abc.abstractmethod
    def disable_provider(self, *, provider_id: int) -> None:
        pass

    @rpc_method
    @abc.abstractmethod
    def change_scim(
        self, *, user_id: int, provider_id: int, enabled: bool, allow_unlinked: bool
    ) -> None:
        pass

    @rpc_method
    @abc.abstractmethod
    def update_provider_config(
        self, organization_id: int, auth_provider_id: int, config: Mapping[str, Any]
    ) -> None:
        pass


auth_service: AuthService = cast(AuthService, AuthService.create_delegation())
