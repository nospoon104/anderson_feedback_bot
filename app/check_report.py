import asyncio
from datetime import datetime, timedelta

from app.db.repositories.survey_repository import SurveyRepository
from app.db.session import AsyncSessionLocal
from app.services.report_service import ReportService


async def check_report():
    async with AsyncSessionLocal() as session:
        survey_repository = SurveyRepository(session)
        report_service = ReportService(survey_repository)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        report = await report_service.build_cafe_report(
            cafe_id=1,
            start_date=start_date,
            end_date=end_date,
        )

        print("REPORT:")
        print(f"Cafe ID: {report.cafe_id}")
        print(f"Period: {report.period.start_date} -> {report.period.end_date}")
        print(f"Total surveys: {report.summary.total_surveys}")
        print(f"Average score: {report.summary.average_score}")
        print(f"Average percent: {report.summary.average_percent}")

        print("\nDistribution:")
        print(f"100%: {report.summary.distribution.score_100_count}")
        print(f"75%: {report.summary.distribution.score_75_count}")
        print(f"50%: {report.summary.distribution.score_50_count}")
        print(f"25%: {report.summary.distribution.score_25_count}")
        print(f"0%: {report.summary.distribution.score_0_count}")

        print("\nQuestion stats:")
        print(f"Q1 yes%: {report.q1_stats.yes_percent}")
        print(f"Q2 yes%: {report.q2_stats.yes_percent}")
        print(f"Q3 yes%: {report.q3_stats.yes_percent}")
        print(f"Q4 yes%: {report.q4_stats.yes_percent}")

        print("\nComparison:")
        print(f"Current average percent: {report.comparison.current_average_percent}")
        print(f"Previous average percent: {report.comparison.previous_average_percent}")
        print(f"Delta: {report.comparison.delta_percent_points}")


if __name__ == "__main__":
    asyncio.run(check_report())
