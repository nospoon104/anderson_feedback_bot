import asyncio

from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.survey_repository import SurveyRepository
from app.db.repositories.user_repository import UserRepository
from app.db.session import AsyncSessionLocal


async def check_data():
    async with AsyncSessionLocal() as session:
        cafe_repository = CafeRepository(session)
        user_repository = UserRepository(session)
        survey_repository = SurveyRepository(session)

        cafes = await cafe_repository.list_all()
        users = await user_repository.list_all()

        print("CAFES:")
        for cafe in cafes:
            print(cafe.id, cafe.name, cafe.code)

        print("\nUSERS:")
        for user in users:
            print(user.id, user.full_name, user.role, user.cafe_id)

        if cafes:
            surveys = await survey_repository.list_by_cafe(cafes[0].id)
            print("\nSURVEYS:")
            for survey in surveys:
                print(
                    survey.id,
                    survey.cafe_id,
                    survey.table_number,
                    survey.q1,
                    survey.q2,
                    survey.q3,
                    survey.q4,
                    survey.comment_text,
                )


if __name__ == "__main__":
    asyncio.run(check_data())
