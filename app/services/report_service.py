from datetime import datetime, time, timedelta

from app.core.constants import SURVEY_QUESTION_LABELS
from app.db.models import Survey
from app.db.repositories.cafe_repository import CafeRepository
from app.db.repositories.survey_repository import SurveyRepository
from app.schemas.report import (
    CafeReportSchema,
    CafeShortReportSchema,
    DistributionComparisonItemSchema,
    NetworkReportSchema,
    PeriodPointSchema,
    QuestionComparisonSchema,
    QuestionStatsSchema,
    ReportComparisonSchema,
    ReportDynamicsSchema,
    ReportPeriodSchema,
    ReportSummarySchema,
    ScoreDistributionSchema,
)
from app.services.ai_comment_service import AICommentService


class ReportService:
    def __init__(
        self,
        survey_repository: SurveyRepository,
        cafe_repository: CafeRepository | None = None,
        ai_comment_service: AICommentService | None = None,
    ):
        self.survey_repository = survey_repository
        self.cafe_repository = cafe_repository
        self.ai_comment_service = ai_comment_service or AICommentService()

    @staticmethod
    def calculate_survey_score(survey: Survey) -> int:
        return int(survey.q1) + int(survey.q2) + int(survey.q3) + int(survey.q4)

    @classmethod
    def calculate_survey_percent(cls, survey: Survey) -> float:
        return (cls.calculate_survey_score(survey) / 4) * 100

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
        start_date: datetime,
        end_date: datetime,
    ) -> tuple[datetime, datetime]:
        delta = end_date - start_date
        previous_end = start_date - timedelta(seconds=1)
        previous_start = previous_end - delta
        return previous_start, previous_end

    @staticmethod
    def _count_comments(comments: list[str]) -> int:
        return len([comment for comment in comments if comment and comment.strip()])

    @staticmethod
    def _distribution_to_dict(distribution: ScoreDistributionSchema) -> dict[str, int]:
        return {
            "100%": distribution.score_100_count,
            "75%": distribution.score_75_count,
            "50%": distribution.score_50_count,
            "25%": distribution.score_25_count,
            "0%": distribution.score_0_count,
        }

    def _build_question_comparisons(
        self,
        current_surveys: list[Survey],
        previous_surveys: list[Survey],
    ) -> list[QuestionComparisonSchema]:
        question_keys = ["q1", "q2", "q3", "q4"]
        comparisons: list[QuestionComparisonSchema] = []

        for question_key in question_keys:
            current_values = [
                getattr(survey, question_key) for survey in current_surveys
            ]
            previous_values = [
                getattr(survey, question_key) for survey in previous_surveys
            ]

            current_stats = self.calculate_question_stats(current_values)
            previous_stats = self.calculate_question_stats(previous_values)

            comparisons.append(
                QuestionComparisonSchema(
                    question_key=question_key,
                    question_label=SURVEY_QUESTION_LABELS[question_key],
                    current_yes_percent=current_stats.yes_percent,
                    previous_yes_percent=previous_stats.yes_percent,
                    delta_percent_points=round(
                        current_stats.yes_percent - previous_stats.yes_percent,
                        2,
                    ),
                )
            )

        return comparisons

    def _build_distribution_comparisons(
        self,
        current_summary: ReportSummarySchema,
        previous_summary: ReportSummarySchema,
    ) -> list[DistributionComparisonItemSchema]:
        current_distribution = self._distribution_to_dict(current_summary.distribution)
        previous_distribution = self._distribution_to_dict(
            previous_summary.distribution
        )

        labels = ["100%", "75%", "50%", "25%", "0%"]

        return [
            DistributionComparisonItemSchema(
                label=label,
                current_count=current_distribution[label],
                previous_count=previous_distribution[label],
                delta_count=current_distribution[label] - previous_distribution[label],
            )
            for label in labels
        ]

    async def _build_weekly_points_for_cafe(
        self,
        cafe_id: int,
        end_date: datetime,
        weeks: int = 4,
    ) -> list[PeriodPointSchema]:
        points: list[PeriodPointSchema] = []

        current_end = end_date
        for _ in range(weeks):
            current_start = datetime.combine(
                (current_end - timedelta(days=6)).date(),
                time.min,
            )

            surveys = await self.survey_repository.list_by_cafe_and_period(
                cafe_id=cafe_id,
                start_date=current_start,
                end_date=current_end,
            )
            comments = await self.survey_repository.list_comments_by_cafe_and_period(
                cafe_id=cafe_id,
                start_date=current_start,
                end_date=current_end,
            )
            summary = self.calculate_summary(surveys)

            points.append(
                PeriodPointSchema(
                    label=f"{current_start:%d.%m}-{current_end:%d.%m}",
                    start_date=current_start,
                    end_date=current_end,
                    total_surveys=summary.total_surveys,
                    average_percent=summary.average_percent,
                    comments_count=self._count_comments(comments),
                )
            )

            current_end = current_start - timedelta(seconds=1)

        points.reverse()
        return points

    async def _build_weekly_points_for_network(
        self,
        end_date: datetime,
        weeks: int = 4,
    ) -> list[PeriodPointSchema]:
        if self.cafe_repository is None:
            return []

        cafes = await self.cafe_repository.list_all()
        points: list[PeriodPointSchema] = []

        current_end = end_date
        for _ in range(weeks):
            current_start = datetime.combine(
                (current_end - timedelta(days=6)).date(),
                time.min,
            )

            period_surveys: list[Survey] = []
            comments_count = 0

            for cafe in cafes:
                surveys = await self.survey_repository.list_by_cafe_and_period(
                    cafe_id=cafe.id,
                    start_date=current_start,
                    end_date=current_end,
                )
                comments = (
                    await self.survey_repository.list_comments_by_cafe_and_period(
                        cafe_id=cafe.id,
                        start_date=current_start,
                        end_date=current_end,
                    )
                )
                period_surveys.extend(surveys)
                comments_count += self._count_comments(comments)

            summary = self.calculate_summary(period_surveys)

            points.append(
                PeriodPointSchema(
                    label=f"{current_start:%d.%m}-{current_end:%d.%m}",
                    start_date=current_start,
                    end_date=current_end,
                    total_surveys=summary.total_surveys,
                    average_percent=summary.average_percent,
                    comments_count=comments_count,
                )
            )

            current_end = current_start - timedelta(seconds=1)

        points.reverse()
        return points

    async def _build_monthly_points_for_cafe(
        self,
        cafe_id: int,
        end_date: datetime,
        months: int = 3,
    ) -> list[PeriodPointSchema]:
        points: list[PeriodPointSchema] = []

        year = end_date.year
        month = end_date.month

        for _ in range(months):
            month_start = datetime(year, month, 1, 0, 0, 0)

            if month == 12:
                next_month_start = datetime(year + 1, 1, 1, 0, 0, 0)
            else:
                next_month_start = datetime(year, month + 1, 1, 0, 0, 0)

            month_end = next_month_start - timedelta(seconds=1)

            surveys = await self.survey_repository.list_by_cafe_and_period(
                cafe_id=cafe_id,
                start_date=month_start,
                end_date=month_end,
            )
            comments = await self.survey_repository.list_comments_by_cafe_and_period(
                cafe_id=cafe_id,
                start_date=month_start,
                end_date=month_end,
            )
            summary = self.calculate_summary(surveys)

            points.append(
                PeriodPointSchema(
                    label=f"{month:02d}.{year}",
                    start_date=month_start,
                    end_date=month_end,
                    total_surveys=summary.total_surveys,
                    average_percent=summary.average_percent,
                    comments_count=self._count_comments(comments),
                )
            )

            month -= 1
            if month == 0:
                month = 12
                year -= 1

        points.reverse()
        return points

    async def _build_monthly_points_for_network(
        self,
        end_date: datetime,
        months: int = 3,
    ) -> list[PeriodPointSchema]:
        if self.cafe_repository is None:
            return []

        cafes = await self.cafe_repository.list_all()
        points: list[PeriodPointSchema] = []

        year = end_date.year
        month = end_date.month

        for _ in range(months):
            month_start = datetime(year, month, 1, 0, 0, 0)

            if month == 12:
                next_month_start = datetime(year + 1, 1, 1, 0, 0, 0)
            else:
                next_month_start = datetime(year, month + 1, 1, 0, 0, 0)

            month_end = next_month_start - timedelta(seconds=1)

            period_surveys: list[Survey] = []
            comments_count = 0

            for cafe in cafes:
                surveys = await self.survey_repository.list_by_cafe_and_period(
                    cafe_id=cafe.id,
                    start_date=month_start,
                    end_date=month_end,
                )
                comments = (
                    await self.survey_repository.list_comments_by_cafe_and_period(
                        cafe_id=cafe.id,
                        start_date=month_start,
                        end_date=month_end,
                    )
                )
                period_surveys.extend(surveys)
                comments_count += self._count_comments(comments)

            summary = self.calculate_summary(period_surveys)

            points.append(
                PeriodPointSchema(
                    label=f"{month:02d}.{year}",
                    start_date=month_start,
                    end_date=month_end,
                    total_surveys=summary.total_surveys,
                    average_percent=summary.average_percent,
                    comments_count=comments_count,
                )
            )

            month -= 1
            if month == 0:
                month = 12
                year -= 1

        points.reverse()
        return points

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

        comments = await self.survey_repository.list_comments_by_cafe_and_period(
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
        previous_comments = (
            await self.survey_repository.list_comments_by_cafe_and_period(
                cafe_id=cafe_id,
                start_date=previous_start,
                end_date=previous_end,
            )
        )

        previous_summary = self.calculate_summary(previous_surveys)

        comparison = ReportComparisonSchema(
            current_average_percent=summary.average_percent,
            previous_average_percent=previous_summary.average_percent,
            delta_percent_points=round(
                summary.average_percent - previous_summary.average_percent,
                2,
            ),
            current_total_surveys=summary.total_surveys,
            previous_total_surveys=previous_summary.total_surveys,
            previous_period_start_date=previous_start,
            previous_period_end_date=previous_end,
            current_comments_count=self._count_comments(comments),
            previous_comments_count=self._count_comments(previous_comments),
        )

        question_comparisons = self._build_question_comparisons(
            current_surveys=surveys,
            previous_surveys=previous_surveys,
        )

        distribution_comparisons = self._build_distribution_comparisons(
            current_summary=summary,
            previous_summary=previous_summary,
        )

        weekly_points = await self._build_weekly_points_for_cafe(
            cafe_id=cafe_id,
            end_date=end_date,
            weeks=4,
        )
        monthly_points = await self._build_monthly_points_for_cafe(
            cafe_id=cafe_id,
            end_date=end_date,
            months=3,
        )

        dynamics = ReportDynamicsSchema(
            weekly_points=weekly_points,
            monthly_points=monthly_points,
        )

        try:
            ai_summary = await self.ai_comment_service.analyze_comments(comments)
        except Exception:
            ai_summary = (
                "AI-анализ комментариев\n\n"
                "Не удалось выполнить AI-анализ комментариев для этого отчёта."
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
            comments=comments,
            ai_summary=ai_summary,
            comments_count=self._count_comments(comments),
            previous_comments_count=self._count_comments(previous_comments),
            question_comparisons=question_comparisons,
            distribution_comparisons=distribution_comparisons,
            dynamics=dynamics,
        )

    async def build_network_report(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> NetworkReportSchema:
        if self.cafe_repository is None:
            raise ValueError("CafeRepository is required for network report")

        cafes = await self.cafe_repository.list_all()

        all_surveys: list[Survey] = []
        all_comments: list[str] = []
        previous_all_surveys: list[Survey] = []
        previous_all_comments: list[str] = []
        cafe_reports: list[CafeShortReportSchema] = []

        previous_start, previous_end = self.get_previous_period(start_date, end_date)

        for cafe in cafes:
            cafe_surveys = await self.survey_repository.list_by_cafe_and_period(
                cafe_id=cafe.id,
                start_date=start_date,
                end_date=end_date,
            )
            cafe_comments = (
                await self.survey_repository.list_comments_by_cafe_and_period(
                    cafe_id=cafe.id,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            previous_cafe_surveys = (
                await self.survey_repository.list_by_cafe_and_period(
                    cafe_id=cafe.id,
                    start_date=previous_start,
                    end_date=previous_end,
                )
            )

            all_surveys.extend(cafe_surveys)
            all_comments.extend(cafe_comments)
            previous_all_surveys.extend(previous_cafe_surveys)

            cafe_summary = self.calculate_summary(cafe_surveys)
            previous_cafe_summary = self.calculate_summary(previous_cafe_surveys)

            cafe_reports.append(
                CafeShortReportSchema(
                    cafe_id=cafe.id,
                    cafe_name=cafe.name,
                    total_surveys=cafe_summary.total_surveys,
                    average_percent=cafe_summary.average_percent,
                    comments_count=self._count_comments(cafe_comments),
                    previous_average_percent=previous_cafe_summary.average_percent,
                    delta_percent_points=round(
                        cafe_summary.average_percent
                        - previous_cafe_summary.average_percent,
                        2,
                    ),
                )
            )

        for cafe in cafes:
            comments = await self.survey_repository.list_comments_by_cafe_and_period(
                cafe_id=cafe.id,
                start_date=previous_start,
                end_date=previous_end,
            )
            previous_all_comments.extend(comments)

        cafe_reports.sort(
            key=lambda cafe_report: (
                cafe_report.average_percent,
                cafe_report.total_surveys,
            ),
            reverse=True,
        )

        summary = self.calculate_summary(all_surveys)
        previous_summary = self.calculate_summary(previous_all_surveys)

        q1_stats = self.calculate_question_stats([survey.q1 for survey in all_surveys])
        q2_stats = self.calculate_question_stats([survey.q2 for survey in all_surveys])
        q3_stats = self.calculate_question_stats([survey.q3 for survey in all_surveys])
        q4_stats = self.calculate_question_stats([survey.q4 for survey in all_surveys])

        question_comparisons = self._build_question_comparisons(
            current_surveys=all_surveys,
            previous_surveys=previous_all_surveys,
        )

        distribution_comparisons = self._build_distribution_comparisons(
            current_summary=summary,
            previous_summary=previous_summary,
        )

        weekly_points = await self._build_weekly_points_for_network(
            end_date=end_date,
            weeks=4,
        )
        monthly_points = await self._build_monthly_points_for_network(
            end_date=end_date,
            months=3,
        )

        dynamics = ReportDynamicsSchema(
            weekly_points=weekly_points,
            monthly_points=monthly_points,
        )

        try:
            ai_summary = await self.ai_comment_service.analyze_comments(all_comments)
        except Exception:
            ai_summary = (
                "AI-анализ комментариев\n\n"
                "Не удалось выполнить AI-анализ комментариев для этого отчёта."
            )

        return NetworkReportSchema(
            period=ReportPeriodSchema(
                start_date=start_date,
                end_date=end_date,
            ),
            total_cafes=len(cafes),
            total_surveys=summary.total_surveys,
            average_score=summary.average_score,
            average_percent=summary.average_percent,
            distribution=summary.distribution,
            q1_stats=q1_stats,
            q2_stats=q2_stats,
            q3_stats=q3_stats,
            q4_stats=q4_stats,
            cafes=cafe_reports,
            ai_summary=ai_summary,
            comments_count=self._count_comments(all_comments),
            previous_comments_count=self._count_comments(previous_all_comments),
            question_comparisons=question_comparisons,
            distribution_comparisons=distribution_comparisons,
            dynamics=dynamics,
        )
