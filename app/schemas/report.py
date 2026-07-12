from datetime import datetime

from pydantic import BaseModel, Field


class QuestionStatsSchema(BaseModel):
    yes_count: int
    no_count: int
    yes_percent: float


class ScoreDistributionSchema(BaseModel):
    score_100_count: int
    score_75_count: int
    score_50_count: int
    score_25_count: int
    score_0_count: int


class ReportSummarySchema(BaseModel):
    total_surveys: int
    average_score: float
    average_percent: float
    distribution: ScoreDistributionSchema


class ReportPeriodSchema(BaseModel):
    start_date: datetime
    end_date: datetime


class ReportComparisonSchema(BaseModel):
    current_average_percent: float
    previous_average_percent: float
    delta_percent_points: float
    current_total_surveys: int
    previous_total_surveys: int
    previous_period_start_date: datetime
    previous_period_end_date: datetime
    current_comments_count: int = 0
    previous_comments_count: int = 0


class MetricDeltaSchema(BaseModel):
    current_value: float
    previous_value: float
    delta_value: float


class QuestionComparisonSchema(BaseModel):
    question_key: str
    question_label: str
    current_yes_percent: float
    previous_yes_percent: float
    delta_percent_points: float


class DistributionComparisonItemSchema(BaseModel):
    label: str
    current_count: int
    previous_count: int
    delta_count: int


class PeriodPointSchema(BaseModel):
    label: str
    start_date: datetime
    end_date: datetime
    total_surveys: int
    average_percent: float
    comments_count: int


class CafeComparisonItemSchema(BaseModel):
    cafe_id: int
    cafe_name: str
    total_surveys: int
    average_percent: float
    comments_count: int
    previous_average_percent: float
    delta_percent_points: float


class ReportDynamicsSchema(BaseModel):
    weekly_points: list[PeriodPointSchema] = Field(default_factory=list)
    monthly_points: list[PeriodPointSchema] = Field(default_factory=list)


class CafeReportSchema(BaseModel):
    cafe_id: int
    period: ReportPeriodSchema
    summary: ReportSummarySchema
    q1_stats: QuestionStatsSchema
    q2_stats: QuestionStatsSchema
    q3_stats: QuestionStatsSchema
    q4_stats: QuestionStatsSchema
    comparison: ReportComparisonSchema | None = None
    comments: list[str] = Field(default_factory=list)
    ai_summary: str | None = None
    comments_count: int = 0
    previous_comments_count: int = 0
    question_comparisons: list[QuestionComparisonSchema] = Field(default_factory=list)
    distribution_comparisons: list[DistributionComparisonItemSchema] = Field(
        default_factory=list
    )
    dynamics: ReportDynamicsSchema | None = None


class CafeShortReportSchema(BaseModel):
    cafe_id: int
    cafe_name: str
    total_surveys: int
    average_percent: float
    comments_count: int = 0
    previous_average_percent: float = 0.0
    delta_percent_points: float = 0.0


class NetworkReportSchema(BaseModel):
    period: ReportPeriodSchema
    total_cafes: int
    total_surveys: int
    average_score: float
    average_percent: float
    distribution: ScoreDistributionSchema
    q1_stats: QuestionStatsSchema
    q2_stats: QuestionStatsSchema
    q3_stats: QuestionStatsSchema
    q4_stats: QuestionStatsSchema
    cafes: list[CafeShortReportSchema]
    ai_summary: str | None = None
    comments_count: int = 0
    previous_comments_count: int = 0
    question_comparisons: list[QuestionComparisonSchema] = Field(default_factory=list)
    distribution_comparisons: list[DistributionComparisonItemSchema] = Field(
        default_factory=list
    )
    dynamics: ReportDynamicsSchema | None = None
