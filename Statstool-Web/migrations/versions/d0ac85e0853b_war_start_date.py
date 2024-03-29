"""war:start_date

Revision ID: d0ac85e0853b
Revises: 32741d581dff
Create Date: 2021-02-16 23:35:44.796530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0ac85e0853b'
down_revision = '32741d581dff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('war', sa.Column('start_date', sa.String(length=11), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('war', 'start_date')
    # ### end Alembic commands ###
