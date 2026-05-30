from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from app.core.constants import SURVEY_QUESTION_LABELS
from app.schemas.report import CafeReportSchema, NetworkReportSchema


class ExcelReportService:
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _style_header(row) -> None:
        for cell in row:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")

    @staticmethod
    def _auto_width(worksheet) -> None:
        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column_cells[0].column)

            for cell in column_cells:
                value = "" if cell.value is None else str(cell.value)
                if len(value) > max_length:
                    max_length = len(value)

            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 60)

    @staticmethod
    def _add_questions_sheet(workbook: Workbook, report) -> None:
        ws = workbook.create_sheet(title="Questions")
        ws.append(["Вопрос", "Да", "Нет", "Да %"])
        ExcelReportService._style_header(ws[1])

        ws.append(
            [
                SURVEY_QUESTION_LABELS["q1"],
                report.q1_stats.yes_count,
                report.q1_stats.no_count,
                report.q1_stats.yes_percent,
            ]
        )
        ws.append(
            [
                SURVEY_QUESTION_LABELS["q2"],
                report.q2_stats.yes_count,
                report.q2_stats.no_count,
                report.q2_stats.yes_percent,
            ]
        )
        ws.append(
            [
                SURVEY_QUESTION_LABELS["q3"],
                report.q3_stats.yes_count,
                report.q3_stats.no_count,
                report.q3_stats.yes_percent,
            ]
        )
        ws.append(
            [
                SURVEY_QUESTION_LABELS["q4"],
                report.q4_stats.yes_count,
                report.q4_stats.no_count,
                report.q4_stats.yes_percent,
            ]
        )

        self_align_columns = ("A", "B", "C", "D")
        for col in self_align_columns:
            for cell in ws[col]:
                cell.alignment = Alignment(vertical="top", wrap_text=True)

        ExcelReportService._auto_width(ws)

    def build_cafe_report_file(
        self,
        report: CafeReportSchema,
        comments: list[str],
    ) -> Path:
        workbook = Workbook()

        ws = workbook.active
        ws.title = "Summary"

        ws.append(["Параметр", "Значение"])
        self._style_header(ws[1])

        ws.append(["Кафе ID", report.cafe_id])
        ws.append(
            [
                "Период",
                f"{report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}",
            ]
        )
        ws.append(["Всего анкет", report.summary.total_surveys])
        ws.append(["Средний балл", report.summary.average_score])
        ws.append(["Средний процент", report.summary.average_percent])

        ws.append([])
        ws.append(["Распределение оценок", ""])
        ws.append(["100%", report.summary.distribution.score_100_count])
        ws.append(["75%", report.summary.distribution.score_75_count])
        ws.append(["50%", report.summary.distribution.score_50_count])
        ws.append(["25%", report.summary.distribution.score_25_count])
        ws.append(["0%", report.summary.distribution.score_0_count])

        ws.append([])
        ws.append(["Сравнение с предыдущим периодом", ""])
        if report.comparison is not None:
            ws.append(["Текущий период, %", report.comparison.current_average_percent])
            ws.append(
                ["Предыдущий период, %", report.comparison.previous_average_percent]
            )
            ws.append(["Разница, п.п.", report.comparison.delta_percent_points])

        for cell in ws["A"]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        for cell in ws["B"]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

        self._auto_width(ws)
        self._add_questions_sheet(workbook, report)

        comments_ws = workbook.create_sheet(title="Comments")
        comments_ws.append(["Комментарий"])
        self._style_header(comments_ws[1])

        if comments:
            for comment in comments:
                comments_ws.append([comment])
        else:
            comments_ws.append(["Комментариев за выбранный период нет"])

        for cell in comments_ws["A"]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

        self._auto_width(comments_ws)

        file_name = (
            f"cafe_report_{report.cafe_id}_"
            f"{report.period.start_date:%Y-%m-%d}_"
            f"{report.period.end_date:%Y-%m-%d}.xlsx"
        )
        file_path = self.reports_dir / file_name
        workbook.save(file_path)
        return file_path

    def build_network_report_file(
        self,
        report: NetworkReportSchema,
    ) -> Path:
        workbook = Workbook()

        ws = workbook.active
        ws.title = "Summary"

        ws.append(["Параметр", "Значение"])
        self._style_header(ws[1])

        ws.append(
            [
                "Период",
                f"{report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}",
            ]
        )
        ws.append(["Кафе в отчёте", report.total_cafes])
        ws.append(["Всего анкет", report.total_surveys])
        ws.append(["Средний балл", report.average_score])
        ws.append(["Средний процент", report.average_percent])

        ws.append([])
        ws.append(["Распределение оценок", ""])
        ws.append(["100%", report.distribution.score_100_count])
        ws.append(["75%", report.distribution.score_75_count])
        ws.append(["50%", report.distribution.score_50_count])
        ws.append(["25%", report.distribution.score_25_count])
        ws.append(["0%", report.distribution.score_0_count])

        for cell in ws["A"]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        for cell in ws["B"]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

        self._auto_width(ws)
        self._add_questions_sheet(workbook, report)

        cafes_ws = workbook.create_sheet(title="Cafes")
        cafes_ws.append(["ID кафе", "Название кафе", "Анкет", "Средний процент"])
        self._style_header(cafes_ws[1])

        for cafe in report.cafes:
            cafes_ws.append(
                [
                    cafe.cafe_id,
                    cafe.cafe_name,
                    cafe.total_surveys,
                    cafe.average_percent,
                ]
            )

        for column in ("A", "B", "C", "D"):
            for cell in cafes_ws[column]:
                cell.alignment = Alignment(vertical="top", wrap_text=True)

        self._auto_width(cafes_ws)

        file_name = (
            f"network_report_"
            f"{report.period.start_date:%Y-%m-%d}_"
            f"{report.period.end_date:%Y-%m-%d}.xlsx"
        )
        file_path = self.reports_dir / file_name
        workbook.save(file_path)
        return file_path
