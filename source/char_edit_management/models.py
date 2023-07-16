from source.db.db import Base
import sqlalchemy as sa


class Shop(Base):
    __tablename__ = 'shops'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    standard_api_key = sa.Column(sa.String)
    is_active = sa.Column(sa.Boolean)

    def __str__(self):
        return str(self.title)

    def __repr__(self):
        return str(self.title)

