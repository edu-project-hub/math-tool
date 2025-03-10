from flask import Blueprint, request, render_template
from math_utils import factorial, binom_coeff

math_bp = Blueprint('math', __name__)

@math_bp.route("/binom", methods=["GET", "POST"])
def binom():
    result = None
    n = k = ""
    if request.method == "POST":
        n = request.form.get("n", "")
        k = request.form.get("k", "")
        try:
            n_int = int(n)
            k_int = int(k)
            result = binom_coeff(n_int, k_int)
        except ValueError:
            result = "Ungültige Eingabe"
    return render_template("binom.html", result=result, n=n, k=k)

@math_bp.route("/factorial", methods=["GET", "POST"])
def factorial_calc():
    result = None
    n = ""
    if request.method == "POST":
        n = request.form.get("n", "")
        try:
            n_int = int(n)
            result = factorial(n_int)
        except ValueError:
            result = "Ungültige Eingabe"
    return render_template("factorial.html", result=result, n=n)
