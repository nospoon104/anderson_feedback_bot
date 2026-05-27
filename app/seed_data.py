import asyncio
from datetime import datetime, timedelta

from app.core.constants import ROLE_MANAGER, ROLE_SUPERUSER
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.survey_repository import SurveyRepository
from app.db.session import AsyncSessionLocal
from app.schemas.cafe import CafeCreateSchema
from app.schemas.user import UserCreateSchema
from app.services.survey_service import SurveyService


async def seed_data():
    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)
        user_repository = UserRepository(session)
        survey_repository = SurveyRepository(session)

        cafe = await cafe_repository.get_by_code("cafe_center")
        if cafe is None:
            cafe = await cafe_repository.create(
                CafeCreateSchema(
                    name="Кафе Центр",
                    code="cafe_center",
                    address="ул. Центральная, 1",
                )
            )
            print(f"Cafe created: id={cafe.id}, code={cafe.code}")
        else:
            print(f"Cafe already exists: id={cafe.id}, code={cafe.code}")

        manager = await user_repository.get_by_telegram_id(123456789)
        if manager is None:
            manager = await user_repository.create(
                UserCreateSchema(
                    telegram_id=123456789,
                    full_name="Тестовый менеджер",
                    role=ROLE_MANAGER,
                    cafe_id=cafe.id,
                )
            )
            print(
                f"Manager created: id={manager.id}, telegram_id={manager.telegram_id}"
            )
        else:
            print(
                f"Manager already exists: id={manager.id}, telegram_id={manager.telegram_id}"
            )

        superuser = await user_repository.get_by_telegram_id(999999999)
        if superuser is None:
            superuser = await user_repository.create(
                UserCreateSchema(
                    telegram_id=999999999,
                    full_name="Тестовый суперюзер",
                    role=ROLE_SUPERUSER,
                    cafe_id=None,
                )
            )
            print(
                f"Superuser created: id={superuser.id}, telegram_id={superuser.telegram_id}"
            )
        else:
            print(
                f"Superuser already exists: id={superuser.id}, telegram_id={superuser.telegram_id}"
            )

        survey_service = SurveyService(survey_repository)

        survey = await survey_service.create_survey(
            manager=manager,
            visit_datetime=datetime.utcnow() - timedelta(hours=2),
            table_number=12,
            q1=True,
            q2=False,
            q3=True,
            q4=True,
            comment_text="Гость пожаловался, что долго ждал официанта",
        )
        print(f"Survey created: id={survey.id}")


if __name__ == "__main__":
    asyncio.run(seed_data())
