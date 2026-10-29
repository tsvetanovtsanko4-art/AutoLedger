from pathlib import Path

from alembic import command
from alembic.config import Config

from server.config import settings

ALEMBIC_INI = Path(__file__).parents[1] / "alembic.ini"


def test_migrations_match_models(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{tmp_path / 'migrations.db'}")
    config = Config(str(ALEMBIC_INI))

    command.upgrade(config, "head")
    # Fails if a model changed without a matching migration.
    command.check(config)
    command.downgrade(config, "base")
