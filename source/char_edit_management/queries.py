from source.char_edit_management.models import Shop
from source.db.db import async_session
from source.db.queries import BaseQueries
import sqlalchemy as sa


class ShopQueries(BaseQueries):
    model = Shop

    async def fetch_all(self) -> list[Shop]:
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model)
            )
            return result.scalars().all()

    async def get_shop_by_id(self, shop_id: int) -> Shop:
        async with async_session() as session:
            result = await session.execute(
                sa.select(self.model)
                .where(self.model.id == shop_id)
            )
            return result.scalars().one()

