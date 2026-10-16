"""Teste de regressão do comando `db:reset`.

O defeito original: `_drop_all()` usava apenas `metadata.drop_all`, que ignora a
tabela de controle do Alembic (`alembic_version`). Como ela permanecia com a
revisão em `head`, o `upgrade head` seguinte era no-op e o banco ficava só com a
tabela de controle.

O teste roda a CLI em subprocessos (contexto isolado) contra um SQLite temporário
e compara o conjunto de tabelas antes (após `db:migrate`) e depois do reset.
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_manage(*args: str, env: dict[str, str], stdin: str | None = None) -> subprocess.CompletedProcess:
    """Executa `python manage.py <args>` num subprocesso com o env informado."""
    return subprocess.run(
        [sys.executable, "manage.py", *args],
        cwd=PROJECT_ROOT,
        env=env,
        input=stdin,
        text=True,
        capture_output=True,
    )


def _tables(db_path: Path) -> set[str]:
    """Nomes das tabelas existentes no banco SQLite informado."""
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {row[0] for row in rows}


def test_db_reset_recreates_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "reset.db"
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite+aiosqlite:///{db_path}",
        "SECRET_KEY": "test-secret",
        "DEBUG": "true",
    }

    migrate = _run_manage("db:migrate", env=env)
    assert migrate.returncode == 0, migrate.stderr
    before = _tables(db_path)
    assert "alembic_version" in before and len(before) > 1, before

    reset = _run_manage("db:reset", env=env, stdin="y\n")
    assert reset.returncode == 0, reset.stderr

    after = _tables(db_path)
    # Sem a correção, `after` conteria apenas `alembic_version`.
    assert after == before, f"schema não foi recriado: {before} != {after}"
    assert "alembic_version" in after
