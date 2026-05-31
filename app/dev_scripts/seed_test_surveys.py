import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.constants import ROLE_MANAGER
from app.db.models import User
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.survey_repository import SurveyRepository
from app.db.session import AsyncSessionLocal
from app.schemas.survey import SurveyCreateSchema


COMMENTS_POOL = [
    "Очень приятное обслуживание.",
    "Все понравилось, спасибо.",
    "Официант помог с выбором.",
    "Блюда были вкусные.",
    "Немного долго ждали заказ.",
    "Хотелось бы быстрее подачу напитков.",
    "Уютно и приятно.",
    "Детям понравилось.",
    "Чисто, комфортно, хорошая атмосфера.",
    "Меню объяснили подробно.",
    "Часть блюд была холодновата.",
    "Официант был очень вежлив.",
    "Хорошее место, придём ещё.",
    "Музыка была громковата.",
    "По еде всё отлично.",
    None,
    None,
    None,
]


def random_visit_datetime(days_back: int = 30) -> datetime:
    now = datetime.utcnow()
    days_delta = random.randint(0, days_back)
    hours_delta = random.randint(0, 13)
    minutes_delta = random.randint(0, 59)

    base = now - timedelta(days=days_delta)
    visit_time = base.replace(
        hour=random.randint(10, 22),
        minute=random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]),
        second=0,
        microsecond=0,
    )
    visit_time = visit_time - timedelta(hours=hours_delta, minutes=minutes_delta)

    if visit_time > now:
        visit_time = now - timedelta(minutes=5)

    return visit_time


def random_answers_by_quality() -> tuple[bool, bool, bool, bool]:
    roll = random.random()

    if roll < 0.55:
        score = 4
    elif roll < 0.82:
        score = 3
    elif roll < 0.94:
        score = 2
    elif roll < 0.985:
        score = 1
    else:
        score = 0

    answers = [True] * score + [False] * (4 - score)
    random.shuffle(answers)
    return answers[0], answers[1], answers[2], answers[3]


async def get_manager_for_cafe(session, cafe_id: int) -> User | None:
    result = await session.execute(
        select(User)
        .where(User.role == ROLE_MANAGER)
        .where(User.cafe_id == cafe_id)
        .where(User.is_active.is_(True))
        .order_by(User.id)
    )
    return result.scalars().first()


async def seed_test_surveys() -> None:
    surveys_per_cafe_raw = input(
        "Сколько анкет сгенерировать на каждое кафе? [30]: "
    ).strip()
    surveys_per_cafe = (
        int(surveys_per_cafe_raw) if surveys_per_cafe_raw.isdigit() else 30
    )

    days_back_raw = input(
        "За сколько последних дней генерировать анкеты? [30]: "
    ).strip()
    days_back = int(days_back_raw) if days_back_raw.isdigit() else 30

    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)
        survey_repository = SurveyRepository(session)

        cafes = await cafe_repository.list_all()
        cafes = [cafe for cafe in cafes if cafe.code != "cafe_center"]

        if not cafes:
            print("Нет кафе для генерации тестовых анкет.")
            return

        total_created = 0

        for cafe in cafes:
            manager = await get_manager_for_cafe(session, cafe.id)
            if manager is None:
                print(
                    f"[SKIP] У кафе id={cafe.id}, name={cafe.name} нет активного менеджера."
                )
                continue

            created_for_cafe = 0

            for _ in range(surveys_per_cafe):
                q1, q2, q3, q4 = random_answers_by_quality()
                survey_data = SurveyCreateSchema(
                    cafe_id=cafe.id,
                    created_by_user_id=manager.id,
                    visit_datetime=random_visit_datetime(days_back=days_back),
                    table_number=random.randint(1, 25),
                    q1=q1,
                    q2=q2,
                    q3=q3,
                    q4=q4,
                    comment_text=random.choice(COMMENTS_POOL),
                )
                await survey_repository.create(survey_data)
                created_for_cafe += 1
                total_created += 1

            print(
                f"[OK] Кафе id={cafe.id}, name={cafe.name}: создано {created_for_cafe} анкет"
            )

        print(f"\nГотово. Всего создано анкет: {total_created}")


if __name__ == "__main__":
    asyncio.run(seed_test_surveys())
