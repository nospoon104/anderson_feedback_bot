from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Survey
from app.schemas.survey import SurveyCreateSchema


class SurveyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: SurveyCreateSchema) -> Survey:
        survey = Survey(
            cafe_id=data.cafe_id,
            created_by_user_id=data.created_by_user_id,
            visit_datetime=data.visit_datetime,
            table_number=data.table_number,
            q1=data.q1,
            q2=data.q2,
            q3=data.q3,
            q4=data.q4,
            comment_text=data.comment_text,
        )
        self.session.add(survey)
        await self.session.commit()
        await self.session.refresh(survey)
        return survey

    async def get_by_id(self, survey_id: int) -> Survey | None:
        result = await self.session.execute(
            select(Survey).where(Survey.id == survey_id)
        )
        return result.scalar_one_or_none()

    async def list_by_cafe(
        self,
        cafe_id: int,
    ) -> list[Survey]:
        result = await self.session.execute(
            select(Survey)
            .where(Survey.cafe_id == cafe_id)
            .order_by(Survey.visit_datetime.desc())
        )
        return list(result.scalars().all())

    async def list_by_cafe_and_period(
        self,
        cafe_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Survey]:
        result = await self.session.execute(
            select(Survey)
            .where(Survey.cafe_id == cafe_id)
            .where(Survey.visit_datetime >= start_date)
            .where(Survey.visit_datetime <= end_date)
            .order_by(Survey.visit_datetime.desc())
        )
        return list(result.scalars().all())

    async def list_comments_by_cafe_and_period(
        self,
        cafe_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> list[str]:
        result = await self.session.execute(
            select(Survey.comment_text)
            .where(Survey.cafe_id == cafe_id)
            .where(Survey.visit_datetime >= start_date)
            .where(Survey.visit_datetime <= end_date)
            .where(Survey.comment_text.is_not(None))
            .where(Survey.comment_text != "")
        )
        return list(result.scalars().all())
