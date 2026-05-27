from pydantic import BaseModel, ConfigDict


class CafeCreateSchema(BaseModel):
    name: str
    code: str
    address: str | None = None


class CafeReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    address: str | None
    is_active: bool
