from datetime import datetime, timedelta

from app.db.models import Survey
from app.db.repositories.survey_repository import SurveyRepository
from app.schemas.report import (
    CafeReportSchema,
    QuestionStatsSchema,
    ReportComparisonSchema,
    ReportPeriodSchema,
    ReportSummarySchema,
    ScoreDistributionSchema,
)


class ReportService:
    def __init__(self, survey_repository: SurveyRepository):
        self.survey_repository = survey_repository

    @staticmethod
    def calculate_survey_score(survey: Survey) -> int:
        return int(survey.q1) + int(survey.q2) + int(survey.q3) + int(survey.q4)

    @classmethod
    def calculate_survey_percent(cls, survey: Survey) -> float:
        score = cls.calculate_survey_score(survey)
        return (score / 4) * 100

    @staticmethod
    def calculate_question_stats(values: list[bool]) -> QuestionStatsSchema:
        total = len(values)
        yes_count = sum(int(value) for value in values)
        no_count = total - yes_count
        yes_percent = (yes_count / total * 100) if total > 0 else 0.0

        return QuestionStatsSchema(
            yes_count=yes_count,
            no_count=no_count,
            yes_percent=round(yes_percent, 2),
        )

    @classmethod
    def calculate_summary(cls, surveys: list[Survey]) -> ReportSummarySchema:
        total_surveys = len(surveys)

        if total_surveys == 0:
            return ReportSummarySchema(
                total_surveys=0,
                average_score=0.0,
                average_percent=0.0,
                distribution=ScoreDistributionSchema(
                    score_100_count=0,
                    score_75_count=0,
                    score_50_count=0,
                    score_25_count=0,
                    score_0_count=0,
                ),
            )

        scores = [cls.calculate_survey_score(survey) for survey in surveys]
        percents = [cls.calculate_survey_percent(survey) for survey in surveys]

        distribution = ScoreDistributionSchema(
            score_100_count=sum(1 for score in scores if score == 4),
            score_75_count=sum(1 for score in scores if score == 3),
            score_50_count=sum(1 for score in scores if score == 2),
            score_25_count=sum(1 for score in scores if score == 1),
            score_0_count=sum(1 for score in scores if score == 0),
        )

        average_score = sum(scores) / total_surveys
        average_percent = sum(percents) / total_surveys

        return ReportSummarySchema(
            total_surveys=total_surveys,
            average_score=round(average_score, 2),
            average_percent=round(average_percent, 2),
            distribution=distribution,
        )

    @staticmethod
    def get_previous_period(
        start_date: datetime, end_date: datetime
    ) -> tuple[datetime, datetime]:
        delta = end_date - start_date
        previous_end = start_date - timedelta(seconds=1)
        previous_start = previous_end - delta
        return previous_start, previous_end

    async def build_cafe_report(
        self,
        cafe_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> CafeReportSchema:
        surveys = await self.survey_repository.list_by_cafe_and_period(
            cafe_id=cafe_id,
            start_date=start_date,
            end_date=end_date,
        )

        summary = self.calculate_summary(surveys)

        q1_stats = self.calculate_question_stats([survey.q1 for survey in surveys])
        q2_stats = self.calculate_question_stats([survey.q2 for survey in surveys])
        q3_stats = self.calculate_question_stats([survey.q3 for survey in surveys])
        q4_stats = self.calculate_question_stats([survey.q4 for survey in surveys])

        previous_start, previous_end = self.get_previous_period(start_date, end_date)
        previous_surveys = await self.survey_repository.list_by_cafe_and_period(
            cafe_id=cafe_id,
            start_date=previous_start,
            end_date=previous_end,
        )
        previous_summary = self.calculate_summary(previous_surveys)

        comparison = ReportComparisonSchema(
            current_average_percent=summary.average_percent,
            previous_average_percent=previous_summary.average_percent,
            delta_percent_points=round(
                summary.average_percent - previous_summary.average_percent, 2
            ),
        )

        return CafeReportSchema(
            cafe_id=cafe_id,
            period=ReportPeriodSchema(
                start_date=start_date,
                end_date=end_date,
            ),
            summary=summary,
            q1_stats=q1_stats,
            q2_stats=q2_stats,
            q3_stats=q3_stats,
            q4_stats=q4_stats,
            comparison=comparison,
        )
