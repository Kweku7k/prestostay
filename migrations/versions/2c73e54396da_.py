"""empty message

Revision ID: 2c73e54396da
Revises: f29252677d1a
Create Date: 2023-08-06 17:57:12.724242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c73e54396da'
down_revision = 'f29252677d1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.VARCHAR(),
               type_=sa.Float(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('balance',
               existing_type=sa.Float(),
               type_=sa.VARCHAR(),
               existing_nullable=True)

    # ### end Alembic commands ###
