from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__)

mgmt_port = os.environ.get("MANAGEMENT_EXTERNAL_PORT", 80)
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
    return render_template("index.html", global_vars=get_app_frontend_globals(), session_info=get_session_info())

if __name__ == "__main__":
    app.run()
