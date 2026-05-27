from datetime import datetime

from app.core.constants import MAX_COMMENT_LENGTH, MAX_TABLE_NUMBER, MIN_TABLE_NUMBER
from app.db.models import Survey, User
from app.db.repositories.survey_repository import SurveyRepository
from app.schemas.survey import SurveyCreateSchema


class SurveyService:
    def __init__(self, survey_repository: SurveyRepository):
        self.survey_repository = survey_repository

    async def create_survey(
        self,
        manager: User,
        visit_datetime: datetime,
        table_number: int,
        q1: bool,
        q2: bool,
        q3: bool,
        q4: bool,
        comment_text: str | None = None,
    ) -> Survey:
        if manager.cafe_id is None:
            raise ValueError("Manager is not assigned to a cafe")

        if visit_datetime > datetime.utcnow():
            raise ValueError("Visit datetime cannot be in the future")

        if not (MIN_TABLE_NUMBER <= table_number <= MAX_TABLE_NUMBER):
            raise ValueError("Invalid table number")

        if comment_text and len(comment_text) > MAX_COMMENT_LENGTH:
            raise ValueError("Comment is too long")

        survey_data = SurveyCreateSchema(
            cafe_id=manager.cafe_id,
            created_by_user_id=manager.id,
            visit_datetime=visit_datetime,
            table_number=table_number,
            q1=q1,
            q2=q2,
            q3=q3,
            q4=q4,
            comment_text=comment_text,
        )

        return await self.survey_repository.create(survey_data)
