from __future__ import with_statement
import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context


config = context.config

fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


from flask import current_app
config.set_main_option(
    'sqlalchemy.url', current_app.config.get(
        'SQLALCHEMY_DATABASE_URI').replace('%', '%%'))
target_meta = current_app.extensions['migrate'].db.metadata



def migration_offli():

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_meta=target_meta, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def migration_onli():

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_meta=target_meta,
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    migration_offli()
else:
    migration_onli()
