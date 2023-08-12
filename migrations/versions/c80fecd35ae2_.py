"""empty message

Revision ID: c80fecd35ae2
Revises: 250b4151cfcb
Create Date: 2023-08-08 15:02:43.547945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c80fecd35ae2'
down_revision = '250b4151cfcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('account',
               existing_type=sa.FLOAT(),
               type_=sa.String(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('account',
               existing_type=sa.String(),
               type_=sa.FLOAT(),
               existing_nullable=True)

    # ### end Alembic commands ###
