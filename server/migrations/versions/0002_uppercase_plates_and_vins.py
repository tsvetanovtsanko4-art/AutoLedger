"""uppercase plates and VINs

The API used to store plates exactly as typed while the availability check
compared upper-case values, so "ca1234ab" and "CA1234AB" could both exist.
Plates and VINs are now normalised on input; bring existing rows in line.

If two cars differ only by case this fails on the unique index, and the
duplicate has to be resolved by hand first.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-29 23:30:00
"""
from alembic import op


revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE cars SET plate = UPPER(TRIM(plate)), vin = UPPER(TRIM(vin))")


def downgrade() -> None:
    pass
