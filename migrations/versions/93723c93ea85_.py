"""empty message

Revision ID: 93723c93ea85
Revises: fe4fee12ded4
Create Date: 2021-01-21 19:34:02.456710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93723c93ea85'
down_revision = 'fe4fee12ded4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('answer', sa.Column('foo', sa.String(length=255), nullable=True))
    op.add_column('answer_images', sa.Column('foo', sa.String(length=255), nullable=True))
    op.add_column('question', sa.Column('foo', sa.String(length=255), nullable=True))
    op.add_column('question_images', sa.Column('foo', sa.String(length=255), nullable=True))
    op.add_column('role', sa.Column('foo', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('foo', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'foo')
    op.drop_column('role', 'foo')
    op.drop_column('question_images', 'foo')
    op.drop_column('question', 'foo')
    op.drop_column('answer_images', 'foo')
    op.drop_column('answer', 'foo')
    # ### end Alembic commands ###
