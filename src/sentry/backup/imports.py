from __future__ import annotations

from io import StringIO
from typing import NamedTuple

import click
from django.apps import apps
from django.core import management, serializers
from django.db import IntegrityError, connection, transaction

from sentry.backup.helpers import EXCLUDED_APPS


class OldImportConfig(NamedTuple):
    """While we are migrating to the new backup system, we need to take care not to break the old
    and relatively untested workflows. This model allows us to stub in the old configs."""

    # Do we allow users to update existing models, or force them to only insert new ones? The old
    # behavior was to allow updates of already included models, but we want to move away from this.
    # TODO(getsentry/team-ospo#170): This is a noop for now, but will be used as we migrate to
    # `INSERT-only` importing logic.
    use_update_instead_of_create: bool = False

    # Old imports use "natural" foreign keys, which in practice only changes how foreign keys into
    # `sentry.User` are represented.
    use_natural_foreign_keys: bool = False


def imports(src, old_config: OldImportConfig, printer=click.echo):
    """CLI command wrapping the `exec_import` functionality."""

    try:
        # Import / export only works in monolith mode with a consolidated db.
        with transaction.atomic("default"):
            for obj in serializers.deserialize(
                "json", src, stream=True, use_natural_keys=old_config.use_natural_foreign_keys
            ):
                if obj.object._meta.app_label not in EXCLUDED_APPS:
                    obj.save()
    # For all database integrity errors, let's warn users to follow our
    # recommended backup/restore workflow before reraising exception. Most of
    # these errors come from restoring on a different version of Sentry or not restoring
    # on a clean install.
    except IntegrityError as e:
        warningText = ">> Are you restoring from a backup of the same version of Sentry?\n>> Are you restoring onto a clean database?\n>> If so then this IntegrityError might be our fault, you can open an issue here:\n>> https://github.com/getsentry/sentry/issues/new/choose"
        printer(
            warningText,
            err=True,
        )
        raise (e)

    sequence_reset_sql = StringIO()

    for app in apps.get_app_configs():
        management.call_command(
            "sqlsequencereset", app.label, "--no-color", stdout=sequence_reset_sql
        )

    with connection.cursor() as cursor:
        cursor.execute(sequence_reset_sql.getvalue())