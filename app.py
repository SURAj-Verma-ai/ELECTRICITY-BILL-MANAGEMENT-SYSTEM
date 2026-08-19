import os
from datetime import datetime

from flask import Flask, render_template, session, redirect, url_for
from dotenv import load_dotenv

from src.data.database import init_db
from src.api.auth_routes import auth_bp
from src.content.homepage import HERO, HIGHLIGHTS, FEATURES_INTRO, FEATURES, ABOUT_INTRO, ABOUT, REVIEWS
from src.content.footer import LINK_GROUPS as FOOTER_LINK_GROUPS, BOTTOM_LINKS as FOOTER_BOTTOM_LINKS
from src.utils.decorators import login_required
from src.extensions import limiter

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

app.register_blueprint(auth_bp)

# Turns on request-counting for every @limiter.limit(...) decorator used in
# the app (see src/api/auth_routes.py). Storage defaults to in-memory,
# which is fine for one dev process; set RATELIMIT_STORAGE_URL in .env
# (e.g. to Redis) once this runs behind more than one server process.
app.config["RATELIMIT_STORAGE_URI"] = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
limiter.init_app(app)


@app.context_processor
def inject_globals():
    # Available to every template (e.g. the footer partial) without each
    # route having to remember to pass it.
    return {
        "current_year": datetime.now().year,
        "footer_link_groups": FOOTER_LINK_GROUPS,
        "footer_bottom_links": FOOTER_BOTTOM_LINKS,
    }


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html", hero=HERO, highlights=HIGHLIGHTS)


@app.route("/features")
def features():
    return render_template("features.html", intro=FEATURES_INTRO, features=FEATURES)


@app.route("/about")
def about():
    return render_template("about.html", intro=ABOUT_INTRO, about=ABOUT, reviews=REVIEWS)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))


if __name__ == "__main__":
    init_db()
    app.run(
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        debug=os.getenv("APP_DEBUG", "True") == "True",
    )
