"""add_words_audio_column

Revision ID: a3b49708c092
Revises: 942efc5aad98
Create Date: 2023-08-16 17:35:14.159582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b49708c092'
down_revision: Union[str, None] = '942efc5aad98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('word_items', sa.Column('audio', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('word_items', 'audio')
    # ### end Alembic commands ###
