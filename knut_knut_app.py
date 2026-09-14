from flask import Flask, render_template, request, g
from urllib.parse import urlencode
from translations import TRANSLATIONS
from model import model

app = Flask(__name__)


@app.before_request
def choose_language():
    requested = request.args.get("lang")
    saved = request.cookies.get("language", "en")
    g.language = requested if requested in ("en", "nb") else saved if saved in ("en", "nb") else "en"


@app.after_request
def remember_language(response):
    if request.args.get("lang") in ("en", "nb"):
        response.set_cookie("language", g.language, max_age=31536000, httponly=True, samesite="Lax")
    return response


def translate(text):
    return TRANSLATIONS.get(text, text) if g.language == "en" else text


@app.context_processor
def language_context():
    args = request.args.to_dict()
    args["lang"] = "nb" if g.language == "en" else "en"
    return {"t": translate, "language": g.language, "language_url": request.path + "?" + urlencode(args)}


ROUTE_META = {
    "A->C->D": {"key": "acd", "label": "A → C → D"},
    "A->C->E": {"key": "ace", "label": "A → C → E"},
    "B->C->D": {"key": "bcd", "label": "B → C → D"},
    "B->C->E": {"key": "bce", "label": "B → C → E"},
}


def _route_results(prediction):
    routes = []
    for route_name, meta in ROUTE_META.items():
        is_best = route_name == prediction.best_route
        prefix = "best_route" if is_best else meta["key"]
        routes.append({
            "name": route_name, "label": meta["label"], "is_best": is_best,
            "time": getattr(prediction, f"{prefix}_time"),
            "lower": getattr(prediction, f"{prefix}_time_lower"),
            "upper": getattr(prediction, f"{prefix}_time_upper"),
        })
    # Shared scale with padding keeps every interval and estimate inside its track.
    values = [float(route[key]) for route in routes for key in ("time", "lower", "upper")]
    padding = max((max(values) - min(values)) * 0.08, 5)
    scale_min = min(values) - padding
    scale_span = max(values) + padding - scale_min
    for route in routes:
        route["interval_left"] = (route["lower"] - scale_min) / scale_span * 100
        route["interval_width"] = (route["upper"] - route["lower"]) / scale_span * 100
        route["estimate_left"] = (route["time"] - scale_min) / scale_span * 100
    return sorted(routes, key=lambda route: route["time"])


@app.route('/')
def get_departure_time():
    return render_template("index.html", selected_hour=8, selected_minute=15)


@app.route("/get_best_route")
def get_route():
    try:
        hour = int(request.args.get("hour", ""))
        minute = int(request.args.get("minute", ""))
        if not (6 <= hour <= 17 and 0 <= minute <= 59):
            raise ValueError
    except (ValueError, TypeError):
        return render_template("index.html", error=translate("Velg et gyldig avreisetidspunkt mellom 06:00 og 17:59."), selected_hour=8, selected_minute=15), 400

    prediction = model(hour, minute)
    routes = _route_results(prediction)
    best = next(route for route in routes if route["is_best"])
    return render_template("results.html", departure=f"{hour:02d}:{minute:02d}", prediction=prediction, routes=routes, best=best, random_time=sum(route["time"] for route in routes) / len(routes))


if __name__ == '__main__':
    app.run(debug=True)
