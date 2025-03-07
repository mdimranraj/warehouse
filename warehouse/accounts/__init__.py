# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_multiauth import MultiAuthenticationPolicy

from warehouse.accounts.auth_policy import (
    BasicAuthAuthenticationPolicy,
    SessionAuthenticationPolicy,
    TwoFactorAuthorizationPolicy,
)
from warehouse.accounts.interfaces import (
    IPasswordBreachedService,
    ITokenService,
    IUserService,
)
from warehouse.accounts.models import DisableReason
from warehouse.accounts.services import (
    HaveIBeenPwnedPasswordBreachedService,
    NullPasswordBreachedService,
    TokenServiceFactory,
    database_login_factory,
)
from warehouse.email import send_password_compromised_email_hibp
from warehouse.errors import BasicAuthBreachedPassword, BasicAuthFailedPassword
from warehouse.macaroons.auth_policy import (
    MacaroonAuthenticationPolicy,
    MacaroonAuthorizationPolicy,
)
from warehouse.rate_limiting import IRateLimiter, RateLimit

__all__ = ["NullPasswordBreachedService", "HaveIBeenPwnedPasswordBreachedService"]


REDIRECT_FIELD_NAME = "next"


def _format_exc_status(exc, message):
    exc.status = f"{exc.status_code} {message}"
    return exc


def _basic_auth_login(username, password, request):
    if request.matched_route.name not in ["forklift.legacy.file_upload"]:
        return

    login_service = request.find_service(IUserService, context=None)
    breach_service = request.find_service(IPasswordBreachedService, context=None)

    userid = login_service.find_userid(username)
    if userid is not None:
        user = login_service.get_user(userid)
        is_disabled, disabled_for = login_service.is_disabled(user.id)
        if is_disabled and disabled_for == DisableReason.CompromisedPassword:
            # This technically violates the contract a little bit, this function is
            # meant to return None if the user cannot log in. However we want to present
            # a different error message than is normal when we're denying the log in
            # because of a compromised password. So to do that, we'll need to raise a
            # HTTPError that'll ultimately get returned to the client. This is OK to do
            # here because we've already successfully authenticated the credentials, so
            # it won't screw up the fall through to other authentication mechanisms
            # (since we wouldn't have fell through to them anyways).
            raise _format_exc_status(
                BasicAuthBreachedPassword(), breach_service.failure_message_plain
            )
        elif login_service.check_password(
            user.id,
            password,
            request.remote_addr,
            tags=["mechanism:basic_auth", "method:auth", "auth_method:basic"],
        ):
            if breach_service.check_password(
                password, tags=["method:auth", "auth_method:basic"]
            ):
                send_password_compromised_email_hibp(request, user)
                login_service.disable_password(
                    user.id, reason=DisableReason.CompromisedPassword
                )
                raise _format_exc_status(
                    BasicAuthBreachedPassword(), breach_service.failure_message_plain
                )
            else:
                login_service.update_user(
                    user.id, last_login=datetime.datetime.utcnow()
                )
                return _authenticate(user.id, request)
        else:
            user.record_event(
                tag="account:login:failure",
                ip_address=request.remote_addr,
                additional={"reason": "invalid_password", "auth_method": "basic"},
            )
            raise _format_exc_status(
                BasicAuthFailedPassword(),
                "Invalid or non-existent authentication information. "
                "See {projecthelp} for more information.".format(
                    projecthelp=request.help_url(_anchor="invalid-auth")
                ),
            )


def _authenticate(userid, request):
    login_service = request.find_service(IUserService, context=None)
    user = login_service.get_user(userid)

    if user is None:
        return

    principals = []

    if user.is_superuser:
        principals.append("group:admins")
    if user.is_moderator or user.is_superuser:
        principals.append("group:moderators")
    if user.is_psf_staff or user.is_superuser:
        principals.append("group:psf_staff")

    # user must have base admin access if any admin permission
    if principals:
        principals.append("group:with_admin_dashboard_access")

    return principals


def _session_authenticate(userid, request):
    if request.matched_route.name in ["forklift.legacy.file_upload"]:
        return

    return _authenticate(userid, request)


def _user(request):
    userid = request.authenticated_userid

    if userid is None:
        return

    login_service = request.find_service(IUserService, context=None)
    return login_service.get_user(userid)


def includeme(config):
    # Register our login service
    config.register_service_factory(database_login_factory, IUserService)

    # Register our token services
    config.register_service_factory(
        TokenServiceFactory(name="password"), ITokenService, name="password"
    )
    config.register_service_factory(
        TokenServiceFactory(name="email"), ITokenService, name="email"
    )
    config.register_service_factory(
        TokenServiceFactory(name="two_factor"), ITokenService, name="two_factor"
    )

    # Register our password breach detection service.
    breached_pw_class = config.maybe_dotted(
        config.registry.settings.get(
            "breached_passwords.backend", HaveIBeenPwnedPasswordBreachedService
        )
    )
    config.register_service_factory(
        breached_pw_class.create_service, IPasswordBreachedService
    )

    # Register our authentication and authorization policies
    config.set_authentication_policy(
        MultiAuthenticationPolicy(
            [
                SessionAuthenticationPolicy(callback=_session_authenticate),
                BasicAuthAuthenticationPolicy(check=_basic_auth_login),
                MacaroonAuthenticationPolicy(callback=_authenticate),
            ]
        )
    )
    config.set_authorization_policy(
        TwoFactorAuthorizationPolicy(
            policy=MacaroonAuthorizationPolicy(policy=ACLAuthorizationPolicy())
        )
    )

    # Add a request method which will allow people to access the user object.
    config.add_request_method(_user, name="user", reify=True)

    # Register the rate limits that we're going to be using for our login
    # attempts and account creation
    user_login_ratelimit_string = config.registry.settings.get(
        "warehouse.account.user_login_ratelimit_string"
    )
    config.register_service_factory(
        RateLimit(user_login_ratelimit_string), IRateLimiter, name="user.login"
    )
    ip_login_ratelimit_string = config.registry.settings.get(
        "warehouse.account.ip_login_ratelimit_string"
    )
    config.register_service_factory(
        RateLimit(ip_login_ratelimit_string), IRateLimiter, name="ip.login"
    )
    global_login_ratelimit_string = config.registry.settings.get(
        "warehouse.account.global_login_ratelimit_string"
    )
    config.register_service_factory(
        RateLimit(global_login_ratelimit_string), IRateLimiter, name="global.login"
    )
    email_add_ratelimit_string = config.registry.settings.get(
        "warehouse.account.email_add_ratelimit_string"
    )
    config.register_service_factory(
        RateLimit(email_add_ratelimit_string), IRateLimiter, name="email.add"
    )
    password_reset_ratelimit_string = config.registry.settings.get(
        "warehouse.account.password_reset_ratelimit_string"
    )
    config.register_service_factory(
        RateLimit(password_reset_ratelimit_string), IRateLimiter, name="password.reset"
    )
