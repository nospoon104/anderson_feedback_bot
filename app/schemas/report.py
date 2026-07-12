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


class TaggedCommentSchema(BaseModel):
    comment: str
    sentiment: str
    tag: str
    short_reason: str
    cafe_name: str | None = None


class TagSummaryItemSchema(BaseModel):
    tag: str
    label: str
    count: int


class CafeTagSummaryItemSchema(BaseModel):
    cafe_id: int
    cafe_name: str
    hall_count: int = 0
    kitchen_food_count: int = 0
    kitchen_speed_count: int = 0
    service_count: int = 0
    bar_count: int = 0
    general_count: int = 0
    total_negative_count: int = 0


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
    tagged_comments: list[TaggedCommentSchema] = Field(default_factory=list)
    negative_tag_summary: list[TagSummaryItemSchema] = Field(default_factory=list)
    previous_negative_tag_summary: list[TagSummaryItemSchema] = Field(
        default_factory=list
    )


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
    executive_ai_summary: str | None = None
    comments_count: int = 0
    previous_comments_count: int = 0
    question_comparisons: list[QuestionComparisonSchema] = Field(default_factory=list)
    distribution_comparisons: list[DistributionComparisonItemSchema] = Field(
        default_factory=list
    )
    dynamics: ReportDynamicsSchema | None = None
    tagged_comments: list[TaggedCommentSchema] = Field(default_factory=list)
    negative_tag_summary: list[TagSummaryItemSchema] = Field(default_factory=list)
    previous_negative_tag_summary: list[TagSummaryItemSchema] = Field(
        default_factory=list
    )
    network_negative_by_cafe: list[CafeTagSummaryItemSchema] = Field(
        default_factory=list
    )
