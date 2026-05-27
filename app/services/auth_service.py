from app.db.models import User
from app.db.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self.user_repository.get_by_telegram_id(telegram_id)
