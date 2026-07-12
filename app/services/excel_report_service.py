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
                horizontal="center",
                vertical="center",
                wrap_text=True,
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
                    cell.alignment = Alignment(vertical="top", wrap_text=True)

    def _auto_width(self, worksheet) -> None:
        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column_cells[0].column)

            for cell in column_cells:
                value = "" if cell.value is None else str(cell.value)
                if len(value) > max_length:
                    max_length = len(value)

            worksheet.column_dimensions[column_letter].width = min(
                max(max_length + 2, 12),
                45,
            )

    @staticmethod
    def _freeze_top(worksheet, cell: str = "A2") -> None:
        worksheet.freeze_panes = cell

    def _style_kpi_table(self, worksheet, start_row: int, end_row: int) -> None:
        for row in range(start_row, end_row + 1):
            worksheet.cell(row=row, column=1).font = self.bold_font
            worksheet.cell(row=row, column=1).fill = self.subtle_fill

    @staticmethod
    def _share_percent(count: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return round(count / total * 100, 2)

    def build_cafe_report_file(self, report: CafeReportSchema) -> str:
        workbook = Workbook()

        summary_ws = workbook.active
        summary_ws.title = "Сводка"

        summary_ws.append(["Показатель", "Значение"])
        self._style_header_row(summary_ws, 1)

        summary_ws.append(["Кафе ID", report.cafe_id])
        summary_ws.append(
            [
                "Текущий период",
                f"{report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}",
            ]
        )
        summary_ws.append(["Анкет в текущем периоде", report.summary.total_surveys])
        summary_ws.append(["Средний балл", report.summary.average_score])
        summary_ws.append(["Средний процент", report.summary.average_percent])
        summary_ws.append(["Комментариев в текущем периоде", report.comments_count])

        if report.comparison is not None:
            summary_ws.append([])
            summary_ws.append(["Сравнение с предыдущим периодом", ""])
            self._style_section_title(summary_ws.cell(summary_ws.max_row, 1))
            self._style_section_title(summary_ws.cell(summary_ws.max_row, 2))

            summary_ws.append(
                [
                    "Предыдущий период",
                    (
                        f"{report.comparison.previous_period_start_date:%d.%m.%Y} - "
                        f"{report.comparison.previous_period_end_date:%d.%m.%Y}"
                    ),
                ]
            )
            summary_ws.append(
                [
                    "Анкет в предыдущем периоде",
                    report.comparison.previous_total_surveys,
                ]
            )
            summary_ws.append(
                [
                    "Комментариев в предыдущем периоде",
                    report.comparison.previous_comments_count,
                ]
            )
            summary_ws.append(
                ["Средний процент — текущий", report.comparison.current_average_percent]
            )
            summary_ws.append(
                [
                    "Средний процент — предыдущий",
                    report.comparison.previous_average_percent,
                ]
            )
            summary_ws.append(["Разница, п.п.", report.comparison.delta_percent_points])
            summary_ws.append(
                [
                    "Примечание",
                    "Сравнение интерпретировать с учётом разницы в количестве анкет между периодами.",
                ]
            )

        self._style_kpi_table(summary_ws, 2, summary_ws.max_row)
        self._freeze_top(summary_ws)

        questions_ws = workbook.create_sheet(title="Вопросы")
        questions_ws.append(
            ["Вопрос", "Да", "Нет", "Да %", "Да % (пред. период)", "Разница, п.п."]
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

        distribution_ws = workbook.create_sheet(title="Распределение")
        distribution_ws.append(
            [
                "Оценка",
                "Текущий период, шт.",
                "Текущий период, %",
                "Предыдущий период, шт.",
                "Предыдущий период, %",
                "Разница, п.п.",
            ]
        )
        self._style_header_row(distribution_ws, 1)

        current_total = report.summary.total_surveys
        previous_total = (
            report.comparison.previous_total_surveys
            if report.comparison is not None
            else 0
        )

        for item in report.distribution_comparisons:
            current_share = self._share_percent(item.current_count, current_total)
            previous_share = self._share_percent(item.previous_count, previous_total)

            distribution_ws.append(
                [
                    item.label,
                    item.current_count,
                    current_share,
                    item.previous_count,
                    previous_share,
                    round(current_share - previous_share, 2),
                ]
            )

        self._freeze_top(distribution_ws)

        dynamics_ws = workbook.create_sheet(title="Динамика")
        dynamics_ws.append(["Недельная динамика", "", "", "", ""])
        self._style_section_title(dynamics_ws["A1"])

        dynamics_ws.append(
            ["Период", "Анкет", "Средний балл", "Средний %", "Комментариев"]
        )
        self._style_header_row(dynamics_ws, 2)

        if report.dynamics is not None:
            for point in report.dynamics.weekly_points:
                average_score = round(point.average_percent / 25, 2)
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        average_score,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        monthly_start_row = dynamics_ws.max_row + 2
        dynamics_ws.cell(row=monthly_start_row, column=1, value="Месячная динамика")
        self._style_section_title(dynamics_ws.cell(row=monthly_start_row, column=1))

        dynamics_ws.append(
            ["Период", "Анкет", "Средний балл", "Средний %", "Комментариев"]
        )
        self._style_header_row(dynamics_ws, monthly_start_row + 1)

        if report.dynamics is not None:
            for point in report.dynamics.monthly_points:
                average_score = round(point.average_percent / 25, 2)
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        average_score,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        self._freeze_top(dynamics_ws)

        comments_ws = workbook.create_sheet(title="Комментарии")
        comments_ws.append(["Комментарий"])
        self._style_header_row(comments_ws, 1)

        if report.comments:
            for comment in report.comments:
                comments_ws.append([comment])
        else:
            comments_ws.append(["Нет комментариев за выбранный период"])

        self._freeze_top(comments_ws)

        ai_ws = workbook.create_sheet(title="AI-анализ")
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
        summary_ws.title = "Сводка"

        summary_ws.append(["Показатель", "Значение"])
        self._style_header_row(summary_ws, 1)

        summary_ws.append(
            [
                "Текущий период",
                f"{report.period.start_date:%d.%m.%Y} - {report.period.end_date:%d.%m.%Y}",
            ]
        )
        summary_ws.append(["Кафе в отчёте", report.total_cafes])
        summary_ws.append(["Анкет в текущем периоде", report.total_surveys])
        summary_ws.append(["Средний балл", report.average_score])
        summary_ws.append(["Средний процент", report.average_percent])
        summary_ws.append(["Комментариев в текущем периоде", report.comments_count])

        summary_ws.append([])
        summary_ws.append(["Примечание по сравнению", ""])
        self._style_section_title(summary_ws.cell(summary_ws.max_row, 1))
        self._style_section_title(summary_ws.cell(summary_ws.max_row, 2))
        summary_ws.append(
            [
                "Логика сравнения",
                "Для каждого кафе и показателя сравнение идёт с предыдущим периодом такой же длины, непосредственно предшествующим текущему.",
            ]
        )

        self._style_kpi_table(summary_ws, 2, summary_ws.max_row)
        self._freeze_top(summary_ws)

        questions_ws = workbook.create_sheet(title="Вопросы")
        questions_ws.append(
            ["Вопрос", "Да", "Нет", "Да %", "Да % (пред. период)", "Разница, п.п."]
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

        distribution_ws = workbook.create_sheet(title="Распределение")
        distribution_ws.append(
            [
                "Оценка",
                "Текущий период, шт.",
                "Текущий период, %",
                "Предыдущий период, шт.",
                "Предыдущий период, %",
                "Разница, п.п.",
            ]
        )
        self._style_header_row(distribution_ws, 1)

        previous_total = 0
        current_total = report.total_surveys

        current_distribution = {
            "100%": report.distribution.score_100_count,
            "75%": report.distribution.score_75_count,
            "50%": report.distribution.score_50_count,
            "25%": report.distribution.score_25_count,
            "0%": report.distribution.score_0_count,
        }

        previous_distribution_map = {
            item.label: item.previous_count for item in report.distribution_comparisons
        }

        previous_total = sum(previous_distribution_map.values())

        for item in report.distribution_comparisons:
            current_share = self._share_percent(item.current_count, current_total)
            previous_share = self._share_percent(item.previous_count, previous_total)

            distribution_ws.append(
                [
                    item.label,
                    item.current_count,
                    current_share,
                    item.previous_count,
                    previous_share,
                    round(current_share - previous_share, 2),
                ]
            )

        self._freeze_top(distribution_ws)

        dynamics_ws = workbook.create_sheet(title="Динамика")
        dynamics_ws.append(["Недельная динамика сети", "", "", "", ""])
        self._style_section_title(dynamics_ws["A1"])

        dynamics_ws.append(
            ["Период", "Анкет", "Средний балл", "Средний %", "Комментариев"]
        )
        self._style_header_row(dynamics_ws, 2)

        if report.dynamics is not None:
            for point in report.dynamics.weekly_points:
                average_score = round(point.average_percent / 25, 2)
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        average_score,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        monthly_start_row = dynamics_ws.max_row + 2
        dynamics_ws.cell(
            row=monthly_start_row, column=1, value="Месячная динамика сети"
        )
        self._style_section_title(dynamics_ws.cell(row=monthly_start_row, column=1))

        dynamics_ws.append(
            ["Период", "Анкет", "Средний балл", "Средний %", "Комментариев"]
        )
        self._style_header_row(dynamics_ws, monthly_start_row + 1)

        if report.dynamics is not None:
            for point in report.dynamics.monthly_points:
                average_score = round(point.average_percent / 25, 2)
                dynamics_ws.append(
                    [
                        point.label,
                        point.total_surveys,
                        average_score,
                        point.average_percent,
                        point.comments_count,
                    ]
                )

        self._freeze_top(dynamics_ws)

        cafes_ws = workbook.create_sheet(title="Кафе")
        cafes_ws.append(
            [
                "ID кафе",
                "Название кафе",
                "Анкет",
                "Средний %",
                "Средний % (пред. период)",
                "Разница, п.п.",
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

        ai_ws = workbook.create_sheet(title="AI-анализ")
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
