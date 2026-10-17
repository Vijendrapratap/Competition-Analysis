"""Convert all naive timestamp columns to timestamptz.

Worker/API code consistently writes timezone-aware UTC datetimes
(datetime.now(timezone.utc)), but most columns were created as
TIMESTAMP WITHOUT TIME ZONE, which asyncpg rejects for aware values.
Standardize on timestamptz; existing naive values are interpreted as UTC.

Revision ID: a1b2c3d4e5f6
Revises: 0872cf973d2a
Create Date: 2026-06-10
"""
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "0872cf973d2a"
branch_labels = None
depends_on = None

_CONVERT = """
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND data_type = 'timestamp without time zone'
      AND table_name <> 'alembic_version'
  LOOP
    EXECUTE format(
      'ALTER TABLE %I ALTER COLUMN %I TYPE timestamptz USING %I AT TIME ZONE ''UTC''',
      r.table_name, r.column_name, r.column_name
    );
  END LOOP;
END $$;
"""

_REVERT = """
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND data_type = 'timestamp with time zone'
      AND table_name <> 'alembic_version'
  LOOP
    EXECUTE format(
      'ALTER TABLE %I ALTER COLUMN %I TYPE timestamp USING %I AT TIME ZONE ''UTC''',
      r.table_name, r.column_name, r.column_name
    );
  END LOOP;
END $$;
"""


def upgrade() -> None:
    op.execute(_CONVERT)


def downgrade() -> None:
    op.execute(_REVERT)
