"""Strona startowa i ścieżka mieszkańca."""
from flask import Blueprint, Response, render_template

from core.domain import AREAS

bp = Blueprint("public", __name__)

EXAMPLE_PROBLEM = (
    "Nasze dzieci z zespołem Downa potrzebują wizyt u wielu specjalistów – kardiologa, logopedy, "
    "endokrynologa. Każda wizyta to inny termin i inna przychodnia, a rodzice są tym zmęczeni."
)


@bp.route("/")
def home():
    return render_template("home.html", example=EXAMPLE_PROBLEM)


@bp.route("/obszary.css")
def area_css():
    """Kolory „nici” obszarów z jednego źródła (core.domain.AREAS); CSP nie pozwala na style inline."""
    css = "".join(f".thread--{slug}{{--thread:{a['color']}}}" for slug, a in AREAS.items())
    return Response(css, mimetype="text/css", headers={"Cache-Control": "public, max-age=3600"})
