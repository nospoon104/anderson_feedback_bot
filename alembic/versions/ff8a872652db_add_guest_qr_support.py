"""add guest qr support

Revision ID: ff8a872652db
Revises: 47a0d5023e73
Create Date: 2026-06-03
"""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ff8a872652db"
down_revision = "47a0d5023e73"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cafes",
        sa.Column("guest_token", sa.String(length=64), nullable=True),
    )

    connection = op.get_bind()
    cafes_table = sa.table(
        "cafes",
        sa.column("id", sa.Integer),
        sa.column("guest_token", sa.String),
    )

    result = connection.execute(sa.select(cafes_table.c.id))
    cafe_ids = [row[0] for row in result]

    for cafe_id in cafe_ids:
        connection.execute(
            cafes_table.update()
            .where(cafes_table.c.id == cafe_id)
            .values(guest_token=uuid4().hex)
        )

    op.alter_column("cafes", "guest_token", nullable=False)
    op.create_unique_constraint(
        "uq_cafes_guest_token",
        "cafes",
        ["guest_token"],
    )

    op.alter_column(
        "surveys",
        "created_by_user_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "surveys",
        "created_by_user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_constraint("uq_cafes_guest_token", "cafes", type_="unique")
    op.drop_column("cafes", "guest_token")
