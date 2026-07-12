from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.schemas.report import CafeReportSchema, NetworkReportSchema


class ExcelReportService:
    def __init__(self) -> None:
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.header_fill = PatternFill("solid", fgColor="1F4E78")
        self.section_fill = PatternFill("solid", fgColor="D9EAF7")
        self.subtle_fill = PatternFill("solid", fgColor="F3F6F9")

        self.header_font = Font(color="FFFFFF", bold=True)
        self.section_font = Font(bold=True)
        self.bold_font = Font(bold=True)

        self.thin_border = Border(
            left=Side(style="thin", color="CCCCCC"),
            right=Side(style="thin", color="CCCCCC"),
            top=Side(style="thin", color="CCCCCC"),
            bottom=Side(style="thin", color="CCCCCC"),
        )

    def _style_header_row(self, worksheet, row_number: int) -> None:
        for cell in worksheet[row_number]:
            cell.fill = self.header_fill
            cell.font = self.header_font
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
            cell.border = self.thin_border

    def _style_section_title(self, cell) -> None:
        cell.fill = self.section_fill
        cell.font = self.section_font
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = self.thin_border

    def _style_data_area(self, worksheet) -> None:
        for row in worksheet.iter_rows():
            for cell in row:
                if cell.value is not None:
                    cell.border = self.thin_border
                    if cell.alignment is None:
                        cell.alignment = Alignment(vertical="top", wrap_text=True)
                    else:
                        cell.alignment = Alignment(
                            horizontal=cell.alignment.horizontal,
                            vertical="top",
                            wrap_text=True,
                        )

    def _auto_width(self, worksheet) -> None:
        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column_cells[0].column)

            for cell in column_cells:
                value = "" if cell.value is None else str(cell.value)
                if len(value) > max_length:
                    max_length = len(value)

            worksheet.column_dimensions[column_letter].width = min(
                max(max_length + 2, 12), 40
            )

    def _freeze_top(self, worksheet, cell: str = "A2") -> None:
        worksheet.freeze_panes = cell

    def _style_kpi_table(self, worksheet, start_row: int, end_row: int) -> None:
        for row in range(start_row, end_row + 1):
            worksheet.cell(row=row, column=1).font = self.bold_font
            worksheet.cell(row=row, column=1).fill = self.subtle_fill

    def build_cafe_report_file(self, report: CafeReportSchema) -> str:
        workbook = Workbook()

        summary_ws = workbook.active
        summary_ws.title = "Summary"

        summary_ws.append(["Показатель", "Значение"])
        self._style_header_row(summary_ws, 1)

        summary_ws.append(["Кафе ID", report.cafe_id])
        summary_ws.append(
            [
                "Период",
                f"{report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}",
            ]
        )
        summary_ws.append(["Всего анкет", report.summary.total_surveys])
        summary_ws.append(["Средний балл", report.summary.average_score])
        summary_ws.append(["Средний процент", report.summary.average_percent])
        summary_ws.append(["Комментариев", report.comments_count])
        summary_ws.append(
            ["Комментариев в прошлом периоде", report.previous_comments_count]
        )

        if report.comparison is not None:
            summary_ws.append([])
            summary_ws.append(["Сравнение с предыдущим периодом", ""])
            self._style_section_title(summary_ws.cell(summary_ws.max_row, 1))
            self._style_section_title(summary_ws.cell(summary_ws.max_row, 2))

            summary_ws.append(
                ["Текущий средний процент", report.comparison.current_average_percent]
            )
            summary_ws.append(
                [
                    "Предыдущий средний процент",
                    report.comparison.previous_average_percent,
                ]
            )
            summary_ws.append(["Δ п.п.", report.comparison.delta_percent_points])

        self._style_kpi_table(summary_ws, 2, summary_ws.max_row)
        self._freeze_top(summary_ws)

        questions_ws = workbook.create_sheet(title="Questions")
        questions_ws.append(
            ["Вопрос", "Да", "Нет", "Да %", "Да % (пред. период)", "Δ п.п."]
        )
        self._style_header_row(questions_ws, 1)

        stats_map = {
            "q1": report.q1_stats,
            "q2": report.q2_stats,
            "q3": report.q3_stats,
            "q4": report.q4_stats,
        }
        comparison_map = {
            item.question_key: item for item in report.question_comparisons
        }

        for question_key, stats in stats_map.items():
            comparison = comparison_map.get(question_key)
            questions_ws.append(
                [
                    comparison.question_label if comparison else question_key,
                    stats.yes_count,
                    stats.no_count,
                    stats.yes_percent,
                    comparison.previous_yes_percent if comparison else 0.0,
                    comparison.delta_percent_points if comparison else 0.0,
                ]
            )

        self._freeze_top(questions_ws)

        distribution_ws = workbook.create_sheet(title="Distribution")
        distribution_ws.append(["Оценка", "Текущий период", "Предыдущий период", "Δ"])
        self._style_header_row(distribution_ws, 1)

        for item in report.distribution_comparisons:
            distribution_ws.append(
                [
                    item.label,
                    item.current_count,
                    item.previous_count,
                    item.delta_count,
                ]
            )

        self._freeze_top(distribution_ws)

        dynamics_ws = workbook.create_sheet(title="Dynamics")
        dynamics_ws.append(["Недельная динамика", "", "", ""])
        self._style_section_title(dynamics_ws["A1"])

        dynamics_ws.append(["Период", "Анкет", "Средний %", "Комментариев"])
        self._style_header_row(dynamics_ws, 2)

        if report.dynamics is not None:
            for point in report.dynamics.weekly_points:
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        monthly_start_row = dynamics_ws.max_row + 2
        dynamics_ws.cell(row=monthly_start_row, column=1, value="Месячная динамика")
        self._style_section_title(dynamics_ws.cell(row=monthly_start_row, column=1))

        dynamics_ws.append(["Период", "Анкет", "Средний %", "Комментариев"])
        self._style_header_row(dynamics_ws, monthly_start_row + 1)

        if report.dynamics is not None:
            for point in report.dynamics.monthly_points:
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        self._freeze_top(dynamics_ws)

        comments_ws = workbook.create_sheet(title="Comments")
        comments_ws.append(["Комментарий"])
        self._style_header_row(comments_ws, 1)

        if report.comments:
            for comment in report.comments:
                comments_ws.append([comment])
        else:
            comments_ws.append(["Нет комментариев за выбранный период"])

        self._freeze_top(comments_ws)

        ai_ws = workbook.create_sheet(title="AI Summary")
        ai_ws.append(["AI-анализ"])
        self._style_header_row(ai_ws, 1)

        ai_lines = (
            report.ai_summary.splitlines()
            if report.ai_summary
            else ["AI-анализ недоступен."]
        )
        for line in ai_lines:
            ai_ws.append([line])

        self._freeze_top(ai_ws)

        for ws in workbook.worksheets:
            self._style_data_area(ws)
            self._auto_width(ws)

        file_name = (
            f"cafe_report_{report.cafe_id}_"
            f"{report.period.start_date:%Y%m%d}_{report.period.end_date:%Y%m%d}.xlsx"
        )
        file_path = self.reports_dir / file_name
        workbook.save(file_path)

        return str(file_path)

    def build_network_report_file(self, report: NetworkReportSchema) -> str:
        workbook = Workbook()

        summary_ws = workbook.active
        summary_ws.title = "Summary"

        summary_ws.append(["Показатель", "Значение"])
        self._style_header_row(summary_ws, 1)

        summary_ws.append(
            [
                "Период",
                f"{report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}",
            ]
        )
        summary_ws.append(["Кафе в отчёте", report.total_cafes])
        summary_ws.append(["Всего анкет", report.total_surveys])
        summary_ws.append(["Средний балл", report.average_score])
        summary_ws.append(["Средний процент", report.average_percent])
        summary_ws.append(["Комментариев", report.comments_count])
        summary_ws.append(
            ["Комментариев в прошлом периоде", report.previous_comments_count]
        )

        self._style_kpi_table(summary_ws, 2, summary_ws.max_row)
        self._freeze_top(summary_ws)

        questions_ws = workbook.create_sheet(title="Questions")
        questions_ws.append(
            ["Вопрос", "Да", "Нет", "Да %", "Да % (пред. период)", "Δ п.п."]
        )
        self._style_header_row(questions_ws, 1)

        stats_map = {
            "q1": report.q1_stats,
            "q2": report.q2_stats,
            "q3": report.q3_stats,
            "q4": report.q4_stats,
        }
        comparison_map = {
            item.question_key: item for item in report.question_comparisons
        }

        for question_key, stats in stats_map.items():
            comparison = comparison_map.get(question_key)
            questions_ws.append(
                [
                    comparison.question_label if comparison else question_key,
                    stats.yes_count,
                    stats.no_count,
                    stats.yes_percent,
                    comparison.previous_yes_percent if comparison else 0.0,
                    comparison.delta_percent_points if comparison else 0.0,
                ]
            )

        self._freeze_top(questions_ws)

        distribution_ws = workbook.create_sheet(title="Distribution")
        distribution_ws.append(["Оценка", "Текущий период", "Предыдущий период", "Δ"])
        self._style_header_row(distribution_ws, 1)

        for item in report.distribution_comparisons:
            distribution_ws.append(
                [
                    item.label,
                    item.current_count,
                    item.previous_count,
                    item.delta_count,
                ]
            )

        self._freeze_top(distribution_ws)

        dynamics_ws = workbook.create_sheet(title="Dynamics")
        dynamics_ws.append(["Недельная динамика сети", "", "", ""])
        self._style_section_title(dynamics_ws["A1"])

        dynamics_ws.append(["Период", "Анкет", "Средний %", "Комментариев"])
        self._style_header_row(dynamics_ws, 2)

        if report.dynamics is not None:
            for point in report.dynamics.weekly_points:
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        monthly_start_row = dynamics_ws.max_row + 2
        dynamics_ws.cell(
            row=monthly_start_row, column=1, value="Месячная динамика сети"
        )
        self._style_section_title(dynamics_ws.cell(row=monthly_start_row, column=1))

        dynamics_ws.append(["Период", "Анкет", "Средний %", "Комментариев"])
        self._style_header_row(dynamics_ws, monthly_start_row + 1)

        if report.dynamics is not None:
            for point in report.dynamics.monthly_points:
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        self._freeze_top(dynamics_ws)

        cafes_ws = workbook.create_sheet(title="Cafes")
        cafes_ws.append(
            [
                "ID кафе",
                "Название кафе",
                "Анкет",
                "Средний %",
                "Средний % (пред. период)",
                "Δ п.п.",
                "Комментариев",
            ]
        )
        self._style_header_row(cafes_ws, 1)

        for cafe in report.cafes:
            cafes_ws.append(
                [
                    cafe.cafe_id,
                    cafe.cafe_name,
                    cafe.total_surveys,
                    cafe.average_percent,
                    cafe.previous_average_percent,
                    cafe.delta_percent_points,
                    cafe.comments_count,
                ]
            )

        self._freeze_top(cafes_ws)

        ai_ws = workbook.create_sheet(title="AI Summary")
        ai_ws.append(["AI-анализ"])
        self._style_header_row(ai_ws, 1)

        ai_lines = (
            report.ai_summary.splitlines()
            if report.ai_summary
            else ["AI-анализ недоступен."]
        )
        for line in ai_lines:
            ai_ws.append([line])

        self._freeze_top(ai_ws)

        for ws in workbook.worksheets:
            self._style_data_area(ws)
            self._auto_width(ws)

        file_name = (
            f"network_report_"
            f"{report.period.start_date:%Y%m%d}_{report.period.end_date:%Y%m%d}.xlsx"
        )
        file_path = self.reports_dir / file_name
        workbook.save(file_path)

        return str(file_path)
