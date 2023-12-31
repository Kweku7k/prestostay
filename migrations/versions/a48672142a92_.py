"""empty message

Revision ID: a48672142a92
Revises: 17bb036864dc
Create Date: 2023-08-17 13:31:41.976430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a48672142a92'
down_revision = '17bb036864dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ledger_entry',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('listing', sa.String(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('balanceBefore', sa.Float(), nullable=True),
    sa.Column('balanceAfter', sa.Float(), nullable=True),
    sa.Column('transactionId', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('ref', sa.String(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('listing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('locationTag', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('roomID', sa.String(), nullable=True),
    sa.Column('listing', sa.String(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('total', sa.Float(), nullable=True),
    sa.Column('charges', sa.Float(), nullable=True),
    sa.Column('balanceBefore', sa.Float(), nullable=True),
    sa.Column('balanceAfter', sa.Float(), nullable=True),
    sa.Column('pending', sa.Boolean(), nullable=True),
    sa.Column('requested', sa.Boolean(), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('account', sa.String(), nullable=True),
    sa.Column('network', sa.String(), nullable=True),
    sa.Column('ledgerEntryId', sa.Integer(), nullable=True),
    sa.Column('ref', sa.String(), nullable=True),
    sa.Column('prestoTransactionId', sa.Integer(), nullable=True),
    sa.Column('channel', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('indexNumber', sa.String(), nullable=True),
    sa.Column('hostel', sa.String(), nullable=True),
    sa.Column('listing', sa.String(), nullable=True),
    sa.Column('roomNumber', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('chatId', sa.String(), nullable=True),
    sa.Column('telegramBot', sa.String(), nullable=True),
    sa.Column('fullAmount', sa.Float(), nullable=True),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.Column('paid', sa.Float(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('callbackUrl', sa.String(), nullable=True),
    sa.Column('availablebalance', sa.Float(), nullable=True),
    sa.Column('percentage', sa.Float(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dailyDisbursal', sa.Boolean(), nullable=True),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('listingId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['listingId'], ['listing.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sub_listing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('listingId', sa.Integer(), nullable=True),
    sa.Column('superListing', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['listingId'], ['listing.id'], ),
    sa.ForeignKeyConstraint(['superListing'], ['listing.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('suggestions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('suggestion', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.Column('listingId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['listingId'], ['listing.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('suggestions')
    op.drop_table('sub_listing')
    op.drop_table('image')
    op.drop_table('users')
    op.drop_table('transactions')
    op.drop_table('listing')
    op.drop_table('ledger_entry')
    # ### end Alembic commands ###
