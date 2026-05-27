from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Cafe
from app.schemas.cafe import CafeCreateSchema


class CafeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: CafeCreateSchema) -> Cafe:
        cafe = Cafe(
            name=data.name,
            code=data.code,
            address=data.address,
        )
        self.session.add(cafe)
        await self.session.commit()
        await self.session.refresh(cafe)
        return cafe

    async def get_by_id(self, cafe_id: int) -> Cafe | None:
        result = await self.session.execute(select(Cafe).where(Cafe.id == cafe_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Cafe | None:
        result = await self.session.execute(select(Cafe).where(Cafe.code == code))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Cafe]:
        result = await self.session.execute(select(Cafe).order_by(Cafe.id))
        return list(result.scalars().all())
