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


def includeme(config):
    # We need to get the value of the Warehouse and Forklift domains, we'll use
    # these to segregate the Warehouse routes from the Forklift routes until
    # Forklift is properly split out into it's own project.
    warehouse = config.get_settings().get("warehouse.domain")
    files_url = config.get_settings()["files.url"]

    # Simple Route for health checks.
    config.add_route("health", "/_health/")

    # Internal route to make it easier to force a particular status for
    # debugging HTTPException templates.
    config.add_route("force-status", r"/_force-status/{status:[45]\d\d}/")

    # Basic global routes
    config.add_route("index", "/", domain=warehouse)
    config.add_route("locale", "/locale/", domain=warehouse)
    config.add_route("robots.txt", "/robots.txt", domain=warehouse)
    config.add_route("opensearch.xml", "/opensearch.xml", domain=warehouse)
    config.add_route("index.sitemap.xml", "/sitemap.xml", domain=warehouse)
    config.add_route("bucket.sitemap.xml", "/{bucket}.sitemap.xml", domain=warehouse)

    # Some static, template driven pages
    config.add_template_view(
        "sitemap", "/sitemap/", "pages/sitemap.html", view_kw={"has_translations": True}
    )
    config.add_template_view(
        "help", "/help/", "pages/help.html", view_kw={"has_translations": True}
    )
    config.add_template_view(
        "security",
        "/security/",
        "pages/security.html",
        view_kw={"has_translations": True},
    )
    # Redirect the old "sponsor PyPI" page to the sponsors page
    config.add_redirect("/sponsor/", "/sponsors/", domain=warehouse)
    config.add_template_view(
        "sponsors",
        "/sponsors/",
        "pages/sponsors.html",
        view_kw={"has_translations": True},
    )

    # Our legal policies
    config.add_policy("terms-of-use", "terms.md")

    # HTML Snippets for including into other pages.
    config.add_route(
        "includes.current-user-indicator",
        "/_includes/current-user-indicator/",
        domain=warehouse,
    )
    config.add_route(
        "includes.flash-messages", "/_includes/flash-messages/", domain=warehouse
    )
    config.add_route(
        "includes.session-notifications",
        "/_includes/session-notifications/",
        domain=warehouse,
    )
    config.add_route(
        "includes.current-user-profile-callout",
        "/_includes/current-user-profile-callout/{username}",
        factory="warehouse.accounts.models:UserFactory",
        traverse="/{username}",
        domain=warehouse,
    )
    config.add_route(
        "includes.edit-project-button",
        "/_includes/edit-project-button/{project_name}",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "includes.profile-actions",
        "/_includes/profile-actions/{username}",
        factory="warehouse.accounts.models:UserFactory",
        traverse="/{username}",
        domain=warehouse,
    )
    config.add_route(
        "includes.profile-public-email",
        "/_includes/profile-public-email/{username}",
        factory="warehouse.accounts.models:UserFactory",
        traverse="/{username}",
        domain=warehouse,
    )
    config.add_route(
        "includes.sidebar-sponsor-logo",
        "/_includes/sidebar-sponsor-logo/",
        domain=warehouse,
    )
    config.add_route(
        "includes.administer-project-include",
        "/_includes/administer-project-include/{project_name}",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )

    # Classifier Routes
    config.add_route("classifiers", "/classifiers/", domain=warehouse)

    # Search Routes
    config.add_route("search", "/search/", domain=warehouse)

    # Stats Routes
    config.add_route("stats", "/stats/", accept="text/html", domain=warehouse)
    config.add_route(
        "stats.json", "/stats/", accept="application/json", domain=warehouse
    )

    # Accounts
    config.add_redirect("/u/{username}/", "/user/{username}/", domain=warehouse)
    config.add_route(
        "accounts.profile",
        "/user/{username}/",
        factory="warehouse.accounts.models:UserFactory",
        traverse="/{username}",
        domain=warehouse,
    )
    config.add_route("accounts.login", "/account/login/", domain=warehouse)
    config.add_route("accounts.two-factor", "/account/two-factor/", domain=warehouse)
    config.add_route(
        "accounts.webauthn-authenticate.options",
        "/account/webauthn-authenticate/options",
        domain=warehouse,
    )
    config.add_route(
        "accounts.webauthn-authenticate.validate",
        "/account/webauthn-authenticate/validate",
        domain=warehouse,
    )
    config.add_route(
        "accounts.reauthenticate", "/account/reauthenticate/", domain=warehouse
    )
    config.add_route(
        "accounts.recovery-code", "/account/recovery-code/", domain=warehouse
    )
    config.add_route("accounts.logout", "/account/logout/", domain=warehouse)
    config.add_route("accounts.register", "/account/register/", domain=warehouse)
    config.add_route(
        "accounts.request-password-reset",
        "/account/request-password-reset/",
        domain=warehouse,
    )
    config.add_route(
        "accounts.reset-password", "/account/reset-password/", domain=warehouse
    )
    config.add_route(
        "accounts.verify-email", "/account/verify-email/", domain=warehouse
    )
    config.add_route(
        "accounts.verify-project-role",
        "/account/verify-project-role/",
        domain=warehouse,
    )
    # Management (views for logged-in users)
    config.add_route("manage.account", "/manage/account/", domain=warehouse)
    config.add_route(
        "manage.account.two-factor", "/manage/account/two-factor/", domain=warehouse
    )
    config.add_route(
        "manage.account.totp-provision",
        "/manage/account/totp-provision",
        domain=warehouse,
    )
    config.add_route(
        "manage.account.totp-provision.image",
        "/manage/account/totp-provision/image",
        domain=warehouse,
    )
    config.add_route(
        "manage.account.webauthn-provision",
        "/manage/account/webauthn-provision",
        domain=warehouse,
    )
    config.add_route(
        "manage.account.webauthn-provision.options",
        "/manage/account/webauthn-provision/options",
        domain=warehouse,
    )
    config.add_route(
        "manage.account.webauthn-provision.validate",
        "/manage/account/webauthn-provision/validate",
        domain=warehouse,
    )
    config.add_route(
        "manage.account.webauthn-provision.delete",
        "/manage/account/webauthn-provision/delete",
        domain=warehouse,
    )
    config.add_route(
        "manage.account.recovery-codes.generate",
        "/manage/account/recovery-codes/generate",
        domain=warehouse,
    )
    config.add_route(
        "manage.account.recovery-codes.regenerate",
        "/manage/account/recovery-codes/regenerate",
        domain=warehouse,
    )
    config.add_route("manage.account.token", "/manage/account/token/", domain=warehouse)
    config.add_route("manage.projects", "/manage/projects/", domain=warehouse)
    config.add_route(
        "manage.project.settings",
        "/manage/project/{project_name}/settings/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.delete_project",
        "/manage/project/{project_name}/delete_project/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.destroy_docs",
        "/manage/project/{project_name}/delete_project_docs/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.releases",
        "/manage/project/{project_name}/releases/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.release",
        "/manage/project/{project_name}/release/{version}/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}/{version}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.roles",
        "/manage/project/{project_name}/collaboration/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.revoke_invite",
        "/manage/project/{project_name}/collaboration/revoke_invite/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.change_role",
        "/manage/project/{project_name}/collaboration/change/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.delete_role",
        "/manage/project/{project_name}/collaboration/delete/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.documentation",
        "/manage/project/{project_name}/documentation/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.history",
        "/manage/project/{project_name}/history/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )
    config.add_route(
        "manage.project.journal",
        "/manage/project/{project_name}/journal/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{project_name}",
        domain=warehouse,
    )

    # Packaging
    config.add_redirect("/p/{name}/", "/project/{name}/", domain=warehouse)
    config.add_route(
        "packaging.project",
        "/project/{name}/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}",
        domain=warehouse,
    )
    config.add_route(
        "packaging.release",
        "/project/{name}/{version}/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}/{version}",
        domain=warehouse,
    )
    config.add_route("packaging.file", files_url)

    # SES Webhooks
    config.add_route("ses.hook", "/_/ses-hook/", domain=warehouse)

    # RSS
    config.add_route("rss.updates", "/rss/updates.xml", domain=warehouse)
    config.add_route("rss.packages", "/rss/packages.xml", domain=warehouse)
    config.add_route(
        "rss.project.releases",
        "/rss/project/{name}/releases.xml",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}/",
        read_only=True,
        domain=warehouse,
    )
    # Integration URLs

    config.add_route(
        "integrations.github.disclose-token",
        "/_/github/disclose-token",
        domain=warehouse,
    )

    config.add_route(
        "integrations.vulnerabilities.osv.report",
        "/_/vulnerabilities/osv/report",
        domain=warehouse,
    )

    # Legacy URLs
    config.add_route("legacy.api.simple.index", "/simple/", domain=warehouse)
    config.add_route(
        "legacy.api.simple.detail",
        "/simple/{name}/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}/",
        read_only=True,
        domain=warehouse,
    )

    config.add_route(
        "legacy.api.json.project",
        "/pypi/{name}/json",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}",
        read_only=True,
        domain=warehouse,
    )
    config.add_route(
        "legacy.api.json.project_slash",
        "/pypi/{name}/json/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}",
        read_only=True,
        domain=warehouse,
    )

    config.add_route(
        "legacy.api.json.release",
        "/pypi/{name}/{version}/json",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}/{version}",
        read_only=True,
        domain=warehouse,
    )
    config.add_route(
        "legacy.api.json.release_slash",
        "/pypi/{name}/{version}/json/",
        factory="warehouse.packaging.models:ProjectFactory",
        traverse="/{name}/{version}",
        read_only=True,
        domain=warehouse,
    )

    # Legacy Action URLs
    # TODO: We should probably add Warehouse routes for these that just error
    #       and direct people to use upload.pypi.org
    config.add_pypi_action_route(
        "legacy.api.pypi.file_upload", "file_upload", domain=warehouse
    )
    config.add_pypi_action_route("legacy.api.pypi.submit", "submit", domain=warehouse)
    config.add_pypi_action_route(
        "legacy.api.pypi.submit_pkg_info", "submit_pkg_info", domain=warehouse
    )
    config.add_pypi_action_route(
        "legacy.api.pypi.doc_upload", "doc_upload", domain=warehouse
    )
    config.add_pypi_action_route("legacy.api.pypi.doap", "doap", domain=warehouse)
    config.add_pypi_action_route(
        "legacy.api.pypi.list_classifiers", "list_classifiers", domain=warehouse
    )
    config.add_pypi_action_route("legacy.api.pypi.search", "search", domain=warehouse)
    config.add_pypi_action_route("legacy.api.pypi.browse", "browse", domain=warehouse)
    config.add_pypi_action_route("legacy.api.pypi.files", "files", domain=warehouse)
    config.add_pypi_action_route("legacy.api.pypi.display", "display", domain=warehouse)

    # Legacy XMLRPC
    config.add_xmlrpc_endpoint(
        "pypi", pattern="/pypi", header="Content-Type:text/xml", domain=warehouse
    )
    config.add_xmlrpc_endpoint(
        "pypi_slash", pattern="/pypi/", header="Content-Type:text/xml", domain=warehouse
    )
    config.add_xmlrpc_endpoint(
        "RPC2", pattern="/RPC2", header="Content-Type:text/xml", domain=warehouse
    )

    # Legacy Documentation
    config.add_route("legacy.docs", config.registry.settings["docs.url"])

    # Legacy Redirects
    config.add_redirect("/pypi/{name}/", "/project/{name}/", domain=warehouse)
    config.add_redirect(
        "/pypi/{name}/{version}/", "/project/{name}/{version}/", domain=warehouse
    )
    config.add_redirect("/pypi/", "/", domain=warehouse)
    config.add_redirect("/packages/{path:.*}", files_url, domain=warehouse)

    # Legacy Action Redirects
    config.add_pypi_action_redirect("rss", "/rss/updates.xml", domain=warehouse)
    config.add_pypi_action_redirect(
        "packages_rss", "/rss/packages.xml", domain=warehouse
    )
