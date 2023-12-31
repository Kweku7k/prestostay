"""empty message

Revision ID: 9333772d1ea6
Revises: 1fb2e3147c01
Create Date: 2023-08-11 15:27:34.942968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9333772d1ea6'
down_revision = '1fb2e3147c01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fullAmount', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('fullAmount')

    # ### end Alembic commands ###
