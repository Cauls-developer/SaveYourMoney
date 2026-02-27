from __future__ import annotations

from functools import partial
from io import BytesIO, StringIO
import csv
from datetime import datetime

from flask import Blueprint, jsonify, request, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .. import state
from ..errors import bad_request
from ..use_cases.list_categories import list_categories
from ..use_cases.list_expenses import list_expenses
from ..use_cases.list_goals import list_goals
from ..use_cases.list_incomes import list_incomes

bp = Blueprint("reports", __name__)


@bp.get("/relatorios/mes")
def report_month():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not month or not year:
        raise bad_request("mes e ano são obrigatórios.")
    report = build_month_report(month, year)
    return jsonify(report)


def build_month_report(month: int, year: int) -> dict:
    expenses = list_expenses(state.expense_repo, month=month, year=year)
    incomes = list_incomes(state.income_repo, month=month, year=year)
    categories = {category.id: category.name for category in list_categories(state.category_repo)}
    total_expenses = sum(expense.value for expense in expenses)
    total_incomes = sum(income.value for income in incomes)
    by_category = {}
    for expense in expenses:
        label = categories.get(expense.category_id, "Sem categoria")
        by_category[label] = by_category.get(label, 0) + expense.value
    goals = list_goals(state.goal_repo, month=month, year=year)
    goal_status = []
    for goal in goals:
        if goal.category_id:
            spent = sum(exp.value for exp in expenses if exp.category_id == goal.category_id)
        else:
            spent = total_expenses
        goal_status.append(
            {
                "id": goal.id,
                "name": goal.name,
                "limit_value": goal.limit_value,
                "spent": round(spent, 2),
                "remaining": round(goal.limit_value - spent, 2),
            }
        )
    return {
        "month": month,
        "year": year,
        "total_expenses": round(total_expenses, 2),
        "total_incomes": round(total_incomes, 2),
        "balance": round(total_incomes - total_expenses, 2),
        "by_category": by_category,
        "goals": goal_status,
    }


@bp.get("/relatorios/mes/csv")
def report_month_csv():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not month or not year:
        raise bad_request("mes e ano são obrigatórios.")
    report = build_month_report(month, year)
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["tipo", "nome", "valor", "extra"])
    writer.writerow(["total", "Total de gastos", report["total_expenses"], ""])
    writer.writerow(["total", "Total de entradas", report["total_incomes"], ""])
    writer.writerow(["total", "Saldo", report["balance"], ""])
    for name, value in report["by_category"].items():
        writer.writerow(["categoria", name, value, ""])
    for goal in report["goals"]:
        writer.writerow(
            ["meta", goal["name"], goal["spent"], f"limite={goal['limit_value']}; restante={goal['remaining']}"]
        )
    output = BytesIO(buffer.getvalue().encode("utf-8"))
    filename = f"relatorio_{month:02d}_{year}.csv"
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name=filename)


def _format_currency_br(value: float) -> str:
    formatted = f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def _format_period(month: int, year: int) -> str:
    return f"{month:02d}/{year}"


def _format_day(day: int | None, month: int, year: int) -> str:
    if day:
        return f"{int(day):02d}/{month:02d}/{year}"
    return f"--/{month:02d}/{year}"


def _build_transactions(expenses, incomes, categories: dict[int, str], month: int, year: int):
    rows = []
    for expense in expenses:
        rows.append(
            {
                "day": int(getattr(expense, "day", 0) or 0),
                "date": _format_day(getattr(expense, "day", None), month, year),
                "description": expense.name or "Gasto",
                "category": categories.get(expense.category_id, "Sem categoria"),
                "kind": "Saída",
                "value": -abs(float(expense.value or 0)),
            }
        )
    for income in incomes:
        rows.append(
            {
                "day": int(getattr(income, "day", 0) or 0),
                "date": _format_day(getattr(income, "day", None), month, year),
                "description": income.name or "Entrada",
                "category": "Entradas",
                "kind": "Entrada",
                "value": abs(float(income.value or 0)),
            }
        )
    rows.sort(key=lambda row: (row["day"], row["kind"], row["description"]))
    return rows


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, document_id: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self._document_id = document_id

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_footer(page_count)
            super().showPage()
        super().save()

    def _draw_footer(self, page_count: int):
        self.setStrokeColor(colors.HexColor("#d7c8d2"))
        self.line(18 * mm, 14 * mm, letter[0] - 18 * mm, 14 * mm)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6f5d6a"))
        self.drawString(18 * mm, 9 * mm, f"Documento: {self._document_id}")
        self.drawCentredString(letter[0] / 2, 9 * mm, "Uso pessoal - Save Your Money")
        self.drawRightString(letter[0] - 18 * mm, 9 * mm, f"Página {self._pageNumber} de {page_count}")


def _build_pdf_story(report: dict, expenses, incomes, categories: dict[int, str], month: int, year: int, issued_at: datetime):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#210123"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#6f5d6a"),
        spaceAfter=2,
    )
    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#6c043c"),
        spaceAfter=6,
        spaceBefore=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
    )

    story = [
        Paragraph("Save Your Money", title_style),
        Paragraph(f"Período do relatório: {_format_period(month, year)}", subtitle_style),
        Paragraph(f"Data de emissão: {issued_at.strftime('%d/%m/%Y %H:%M')}", subtitle_style),
        Spacer(1, 8),
        Paragraph("Resumo financeiro", section_style),
    ]

    balance = float(report["balance"])
    indicator = "Saldo positivo" if balance >= 0 else "Saldo negativo"

    summary_rows = [
        ["Total de entradas", _format_currency_br(report["total_incomes"])],
        ["Total de saídas", _format_currency_br(report["total_expenses"])],
        ["Saldo final", _format_currency_br(balance)],
        ["Indicador", indicator],
    ]
    summary_table = Table(summary_rows, colWidths=[130 * mm, 45 * mm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#f7edf3")),
                ("BACKGROUND", (0, 1), (1, 1), colors.HexColor("#fff4f6")),
                ("BACKGROUND", (0, 2), (1, 2), colors.HexColor("#f2fcfa")),
                ("BACKGROUND", (0, 3), (1, 3), colors.HexColor("#f9f9f9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d7c8d2")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 2), (1, 2), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)

    story.extend([Spacer(1, 10), Paragraph("Lançamentos detalhados", section_style)])
    tx_rows = _build_transactions(expenses, incomes, categories, month, year)
    tx_table_rows = [["Data", "Descrição", "Categoria", "Tipo", "Valor"]]
    if tx_rows:
        for row in tx_rows:
            tx_table_rows.append(
                [
                    row["date"],
                    row["description"],
                    row["category"],
                    row["kind"],
                    _format_currency_br(row["value"]),
                ]
            )
    else:
        tx_table_rows.append(["-", "Sem lançamentos no período", "-", "-", _format_currency_br(0)])

    tx_table = Table(tx_table_rows, colWidths=[22 * mm, 59 * mm, 41 * mm, 24 * mm, 29 * mm], repeatRows=1)
    tx_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#210123")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7c8d2")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbf8fa")]),
                ("ALIGN", (4, 1), (4, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(tx_table)

    story.extend([Spacer(1, 10), Paragraph("Análise por categoria", section_style)])
    category_rows = [["Categoria", "Total", "% das saídas"]]
    by_category = report.get("by_category", {}) or {}
    total_expenses = float(report.get("total_expenses", 0) or 0)
    if by_category and total_expenses > 0:
        for name, value in sorted(by_category.items(), key=lambda item: item[1], reverse=True):
            percent = (float(value) / total_expenses) * 100
            category_rows.append([name, _format_currency_br(value), f"{percent:.1f}%"])
    else:
        category_rows.append(["Sem saídas no período", _format_currency_br(0), "0,0%"])

    category_table = Table(category_rows, colWidths=[95 * mm, 50 * mm, 30 * mm], repeatRows=1)
    category_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6c043c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7c8d2")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fff7fb")]),
                ("ALIGN", (1, 1), (2, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(category_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Espaço reservado para gráfico embutido em versões futuras.", body_style))

    goals = report.get("goals", []) or []
    if goals:
        story.extend([Spacer(1, 8), Paragraph("Metas do período", section_style)])
        goals_rows = [["Meta", "Limite", "Gasto", "Restante"]]
        for goal in goals:
            goals_rows.append(
                [
                    goal["name"],
                    _format_currency_br(goal["limit_value"]),
                    _format_currency_br(goal["spent"]),
                    _format_currency_br(goal["remaining"]),
                ]
            )
        goals_table = Table(goals_rows, colWidths=[70 * mm, 35 * mm, 35 * mm, 35 * mm], repeatRows=1)
        goals_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#355f5f")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7c8d2")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3fbfb")]),
                    ("ALIGN", (1, 1), (3, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(goals_table)

    return story


@bp.get("/relatorios/mes/pdf")
def report_month_pdf():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not month or not year:
        raise bad_request("mes e ano são obrigatórios.")

    report = build_month_report(month, year)
    expenses = list_expenses(state.expense_repo, month=month, year=year)
    incomes = list_incomes(state.income_repo, month=month, year=year)
    categories = {category.id: category.name for category in list_categories(state.category_repo)}

    issued_at = datetime.now()
    document_id = f"SYM-{year}{month:02d}-{issued_at.strftime('%Y%m%d%H%M%S')}"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        title=f"Relatório mensal {_format_period(month, year)}",
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
    )

    story = _build_pdf_story(report, expenses, incomes, categories, month, year, issued_at)
    doc.build(story, canvasmaker=partial(NumberedCanvas, document_id=document_id))

    buffer.seek(0)
    filename = f"relatorio_{month:02d}_{year}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)
