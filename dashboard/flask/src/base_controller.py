from flask import Blueprint, request, render_template, Response, make_response, send_file, redirect
import uuid
import requests
import datetime
import json

from utils import get_session_info, get_app_frontend_globals, check_password, session_data_to_jwt

base_pages = Blueprint("base_pages", __name__)
base_api = Blueprint("base_api", __name__)

#@base_api.route("/api/v1/jobs/<raw_uuid>", methods=['GET'])
#def api_v1_get_job(raw_uuid):
#    try:
#        uuid_obj = uuid.UUID(raw_uuid, version=4)
#        job_data = get_couch()["crab_jobs"][str(uuid_obj)]
#        return Response(json.dumps(job_data), status=200, mimetype='application/json')
#    except ValueError:
#        return Response(json.dumps({
#            "error": "badUUID",
#            "msg": "Invalid UUID " + raw_uuid
#            }), status=400, mimetype='application/json')

@base_pages.route("/login", methods=['GET'])
def page_login():
    err = request.args.get("err", None)
    return render_template("login.html", global_vars=get_app_frontend_globals(), err=err, session_info=get_session_info())

@base_pages.route("/logout", methods=['GET'])
def page_logout():
    response = make_response(redirect("/", code=302))
    response.set_cookie("jwt", "", expires=0)
    return response

@base_api.route("/api/v1/login", methods=['POST'])
def page_login():
    user = request.form.get("username", None)
    password = request.form.get("password", None)
    if check_password(user, password):
        response = make_response(redirect("/", code=302))
        session_info = {
                "sub": user
            }
        response.set_cookie("jwt", session_data_to_jwt(session_info))
        return response
    else:
        return redirect("/login?err=incorrect", code=302)
