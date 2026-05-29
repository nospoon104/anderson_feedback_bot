import asyncio

from app.db.repositories.survey_repository import SurveyRepository
from app.db.session import AsyncSessionLocal


async def check_surveys() -> None:
    async with AsyncSessionLocal() as session:
        survey_repository = SurveyRepository(session)
        surveys = await survey_repository.list_by_cafe(1)

        print("SURVEYS:")
        for survey in surveys:
            print(
                f"id={survey.id}, "
                f"cafe_id={survey.cafe_id}, "
                f"created_by_user_id={survey.created_by_user_id}, "
                f"visit_datetime={survey.visit_datetime}, "
                f"table_number={survey.table_number}, "
                f"q1={survey.q1}, q2={survey.q2}, q3={survey.q3}, q4={survey.q4}, "
                f"comment_text={survey.comment_text}"
            )


if __name__ == "__main__":
    asyncio.run(check_surveys())
