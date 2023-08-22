"""upgrade

Revision ID: 1888016bdc2b
Revises: 540f01afd6dd
Create Date: 2023-08-22 12:08:40.963838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1888016bdc2b'
down_revision: Union[str, None] = '540f01afd6dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feedbacks', sa.Column('translate', sa.String(), nullable=True))
    op.add_column('feedbacks', sa.Column('status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('feedbacks', 'status')
    op.drop_column('feedbacks', 'translate')
    # ### end Alembic commands ###