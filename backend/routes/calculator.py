from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..errors import bad_request
from ..services.finance_service import (
    calculate_basic,
    calculate_compound_interest,
    calculate_discount,
    calculate_monthly_return,
    calculate_simple_interest,
    simulate_debt_payoff,
    simulate_installment,
)

bp = Blueprint("calculator", __name__)


@bp.post("/calculadora")
def calculator():
    data = request.get_json(silent=True) or {}
    operation = (data.get("operation") or "").strip().lower()
    try:
        if operation in {"soma", "subtracao", "multiplicacao", "divisao"}:
            a = float(data.get("a"))
            b = float(data.get("b"))
            result = calculate_basic(operation, a, b)
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "juros_simples":
            result = calculate_simple_interest(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
                months=int(data.get("months")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "juros_compostos":
            result = calculate_compound_interest(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
                months=int(data.get("months")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "parcelamento":
            result = simulate_installment(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
                months=int(data.get("months")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "desconto":
            result = calculate_discount(
                original_value=float(data.get("principal")),
                discount_percent=float(data.get("rate")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "rendimento_mensal":
            result = calculate_monthly_return(
                principal=float(data.get("principal")),
                monthly_rate_percent=float(data.get("rate")),
            )
            return jsonify({"operation": operation, "result": result}), 200
        if operation == "quitacao_divida":
            result = simulate_debt_payoff(
                debt_value=float(data.get("principal")),
                payment_per_month=float(data.get("payment")),
                monthly_rate_percent=float(data.get("rate")),
            )
            return jsonify({"operation": operation, "result": result}), 200
    except (TypeError, ValueError) as exc:
        raise bad_request(f"Parâmetros inválidos para a calculadora. {exc}")
    raise bad_request("Operação de calculadora inválida.")
