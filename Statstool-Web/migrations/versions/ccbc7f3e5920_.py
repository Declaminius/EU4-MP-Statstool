"""empty message

Revision ID: ccbc7f3e5920
Revises: 0cf126545957
Create Date: 2021-04-24 00:02:43.364974

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccbc7f3e5920'
down_revision = '0cf126545957'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('victory_point',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('nation_tag', sa.String(length=3), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['nation_tag'], ['nation.tag'], ),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('victory_point')
    # ### end Alembic commands ###
