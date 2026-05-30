from datetime import datetime

from pydantic import BaseModel


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


class CafeReportSchema(BaseModel):
    cafe_id: int
    period: ReportPeriodSchema
    summary: ReportSummarySchema
    q1_stats: QuestionStatsSchema
    q2_stats: QuestionStatsSchema
    q3_stats: QuestionStatsSchema
    q4_stats: QuestionStatsSchema
    comparison: ReportComparisonSchema | None = None


class CafeShortReportSchema(BaseModel):
    cafe_id: int
    cafe_name: str
    total_surveys: int
    average_percent: float


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
