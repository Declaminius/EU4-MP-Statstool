"""Current MP-Map

Revision ID: 1e691303d014
Revises: e3e33685bc83
Create Date: 2021-04-24 22:58:27.624506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e691303d014'
down_revision = 'e3e33685bc83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mp', sa.Column('current_map_file', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mp', 'current_map_file')
    # ### end Alembic commands ###