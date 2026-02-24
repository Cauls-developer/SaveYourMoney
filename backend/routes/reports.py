from __future__ import annotations

from io import BytesIO, StringIO
import csv

from flask import Blueprint, jsonify, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


@bp.get("/relatorios/mes/pdf")
def report_month_pdf():
    month = request.args.get("mes", type=int)
    year = request.args.get("ano", type=int)
    if not month or not year:
        raise bad_request("mes e ano são obrigatórios.")
    report = build_month_report(month, year)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"Relatório mensal {month:02d}/{year}")
    y -= 30
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Total de gastos: R$ {report['total_expenses']:.2f}")
    y -= 18
    pdf.drawString(50, y, f"Total de entradas: R$ {report['total_incomes']:.2f}")
    y -= 18
    pdf.drawString(50, y, f"Saldo: R$ {report['balance']:.2f}")
    y -= 28
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Gastos por categoria")
    y -= 18
    pdf.setFont("Helvetica", 11)
    if report["by_category"]:
        for name, value in report["by_category"].items():
            pdf.drawString(60, y, f"- {name}: R$ {value:.2f}")
            y -= 16
            if y < 80:
                pdf.showPage()
                y = height - 50
    else:
        pdf.drawString(60, y, "Sem registros.")
        y -= 18
    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Metas do mês")
    y -= 18
    pdf.setFont("Helvetica", 11)
    if report["goals"]:
        for goal in report["goals"]:
            pdf.drawString(
                60,
                y,
                f"- {goal['name']}: gasto R$ {goal['spent']:.2f} / limite R$ {goal['limit_value']:.2f}",
            )
            y -= 16
            if y < 80:
                pdf.showPage()
                y = height - 50
    else:
        pdf.drawString(60, y, "Sem metas.")
        y -= 18
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    filename = f"relatorio_{month:02d}_{year}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)
