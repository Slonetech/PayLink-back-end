"""removed the _ from users.password

Revision ID: 8c79feac9462
Revises: aa2bdfd2d0f0
Create Date: 2023-11-03 11:30:59.311533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c79feac9462'
down_revision = 'aa2bdfd2d0f0'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
