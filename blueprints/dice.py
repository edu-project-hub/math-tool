from flask import Blueprint, request, render_template
from math_utils import factorial, binom_coeff

dice_bp = Blueprint('dice', __name__)

@dice_bp.route("/dice", methods=["GET", "POST"])
def dice():
    result = None
    n = k = faces = ""
    if request.method == "POST":
        n = request.form.get("n", "")
        k = request.form.get("k", "")
        faces = request.form.get("faces", "6")
        try:
            n_int = int(n)
            k_int = int(k)
            faces_int = int(faces)
            if faces_int <= 0:
                result = "Ungültige Eingabe: Seitenzahl muss größer als 0 sein."
            else:
                p = 1 / faces_int
                probability = binom_coeff(n_int, k_int) * (p ** k_int) * ((1 - p) ** (n_int - k_int))
                result = probability
        except ValueError:
            result = "Ungültige Eingabe"
    return render_template("dice.html", result=result, n=n, k=k, faces=faces)
