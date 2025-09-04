from flask import Blueprint, request, render_template, Response, make_response, send_file, redirect, current_app, send_from_directory
import uuid
import requests
import datetime
import json
import os
import glob

from werkzeug.utils import secure_filename
from utils import get_session_info, get_app_frontend_globals, check_password, session_data_to_jwt, publish_message

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

@base_api.route("/api/v1/upload_model", methods=['POST'])
def api_upload_model():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}
    file = request.files['file']
    if file.filename == '':
        return {"error": "No file selected"}
    if file:
        filename = secure_filename(file.filename)
        models_dir = current_app.config["UPLOAD_FOLDER"] + "/models"
        os.makedirs(models_dir, exist_ok=True)
        file.save(os.path.join(models_dir, filename))
        print("Uploaded file!")
        return redirect("/")

@base_api.route("/api/v1/upload_frame", methods=['POST'])
def api_upload_frame():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}
    file = request.files['file']
    if file.filename == '':
        return {"error": "No file selected"}
    if file:
        dts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = "frame_" + dts + ".jpg"
        file.save(os.path.join("/app/temp", filename))


        list_of_files = glob.glob("/app/temp/frame_*.jpg")
        if len(list_of_files) != 0:
            list_of_files.sort(key=lambda x: os.path.getctime(x))
            #print(list_of_files)
            if len(list_of_files) > 3:
                for filename in list_of_files[:-3]:
                    os.remove(filename)

        return {"status": "ok"}

@base_api.route("/api/v1/status", methods=['GET'])
def api_get_status():
    status_msg = {"status": "error"}
    for i in range(5):
        try:
            with open("status.json", "r") as file:
                status_msg = json.loads(file.read())
            break
        except IOError:
            pass
    return status_msg

@base_api.route("/api/v1/asea2-camera-if/status", methods=['GET'])
def api_get_asea2_camera_if_status():
    response = requests.get("http://host.docker.internal:8082/status").json()
    return response

@base_api.route("/api/v1/config", methods=['GET'])
def api_get_config():
    config_val = {}
    for i in range(5):
        try:
            with open("config.json", "r") as file:
                config_val = json.loads(file.read())
            break
        except IOError:
            pass
    return config_val

@base_api.route("/api/v1/status", methods=['POST'])
def api_set_status():
    #if current_app.config["PUSH_SECRET"] == :
    status_msg = request.get_json()
    auth_header = request.headers.get("Authorization")
    if auth_header is not None:
        auth_header_components = auth_header.split(" ")
        if len(auth_header_components) > 1:
            if auth_header_components[0].lower() == "bearer":
                raw_token = auth_header_components[1]
                if raw_token == current_app.config["PUSH_SECRET"]:
                    for i in range(5):
                        try:
                            with open("status.json", "w") as file:
                                file.write(json.dumps(status_msg))
                            break
                        except IOError:
                            time.sleep(1)
                    return {"status": "ok"}

        return {"status": "error", "msg": "Authorization header invalid"}, 403

    return {"status": "error", "msg": "Authorization header missing"}, 401

@base_api.route("/api/v1/set_vision_model", methods=['POST'])
def api_set_vision_model():
    body = {
            "cmd": "set_model",
            "file": request.form.get("model")
        }
    publish_message("vision", body)
    return redirect("/")

@base_api.route("/api/v1/models/<filename>", methods=['GET'])
def api_get_model(filename):
    filename = secure_filename(filename)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'] + "/models", filename)

@base_api.route("/api/v1/tempfile/<filename>", methods=['GET'])
def api_get_tempfile(filename):
    filename = secure_filename(filename)
    return send_from_directory("/app/temp", filename)

@base_api.route("/api/v1/frame", methods=['GET'])
def api_get_lastest_frame():
    list_of_files = glob.glob("/app/temp/frame_*.jpg")
    if len(list_of_files) == 0:
        return {"err": "No frames!"}
    else:
        latest_file = max(list_of_files, key=os.path.getctime)
        #return {"file": os.path.basename(latest_file)}
        return send_from_directory("/app/temp", os.path.basename(latest_file))
