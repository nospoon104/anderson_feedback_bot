from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SurveyCreateSchema(BaseModel):
    cafe_id: int
    created_by_user_id: int
    visit_datetime: datetime
    table_number: int
    q1: bool
    q2: bool
    q3: bool
    q4: bool
    comment_text: str | None = None


class SurveyReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cafe_id: int
    created_by_user_id: int
    visit_datetime: datetime
    table_number: int
    q1: bool
    q2: bool
    q3: bool
    q4: bool
    comment_text: str | None
