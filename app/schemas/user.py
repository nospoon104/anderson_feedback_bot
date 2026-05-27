from pydantic import BaseModel, ConfigDict


class UserCreateSchema(BaseModel):
    telegram_id: int
    full_name: str
    role: str
    cafe_id: int | None = None


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    full_name: str
    role: str
    cafe_id: int | None
    is_active: bool
