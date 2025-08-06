from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import os


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "/app/temp")
app.config["EXTERNAL_PORT"] = os.environ.get("MANAGEMENT_EXTERNAL_PORT", 80)
app.wsgi_app = ProxyFix(app.wsgi_app)

from utils import get_session_info, get_app_frontend_globals
from base_controller import base_pages, base_api

app.register_blueprint(base_pages)
app.register_blueprint(base_api)

@app.errorhandler(404)
def not_found_error_handler(e):
    return render_template("404.html", global_vars=get_app_frontend_globals(), session_info=get_session_info())

@app.route("/")
def home_screen():
    local_vars = {}
    models_dir = app.config["UPLOAD_FOLDER"]
    local_vars["available_models"] = [f for f in os.listdir(models_dir) if os.path.isfile(os.path.join(models_dir, f))]
    return render_template("index.html", global_vars=get_app_frontend_globals(), local_vars=local_vars, session_info=get_session_info())

if __name__ == "__main__":
    app.run()
