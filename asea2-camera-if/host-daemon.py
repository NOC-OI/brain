import os
import signal
from urllib.parse import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import redirect
import random
import sys
import subprocess
import re
import json

class HelperService(object):

    def __init__(self):
        self.url_map = Map([
            Rule('/', endpoint='index'),
            Rule('/status', endpoint='status'),
            Rule('/mount', endpoint='mount'),
            Rule('/destroy', endpoint='destroy')
        ])

        self.service_secret = os.environ.get("INTERNAL_SERVICE_SECRET", ''.join(random.choice('0123456789ABCDEF') for i in range(16))).strip()
        print("Service secret: " + self.service_secret)

    def shutdown_server(self, request):
        pid = os.getpid()
        os.kill(pid, signal.SIGKILL)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f'on_{endpoint}')(request, **values)
        except NotFound as e:
            response = Response("Error 404\nEndpoint not found\n", mimetype="text/plain", status=404)
            return response
        except HTTPException as e:
            return e

    def authenticate_header(self, request):
        response = Response("Error 401\nUnauthorized\n", mimetype="text/plain", status=401)
        if "authorization" in request.headers:
            if request.headers["authorization"].startswith("Bearer "):
                response = Response("Error 403\nForbidden\n", mimetype="text/plain", status=403)
                if request.headers["authorization"][7:].strip() == self.service_secret:
                    return True
        return response

    def on_index(self, request):
        cat_mounts_cp = subprocess.run(["cat", "/proc/mounts"], capture_output=True, text=True)
        res_mount = None
        for line in iter(cat_mounts_cp.stdout.splitlines()):
            sl = line.split(" ")
            if len(sl) > 3:
                if sl[1] == "/mnt/nfs_cam":
                    res_mount = sl[0]
        if res_mount is None:
            response = Response("ASEA2 Camera Interface NFS Mount Helper Service\nVersion 0.0\n\nNo NFS camera mounted!\n", mimetype="text/plain")
        else:
            response = Response("ASEA2 Camera Interface NFS Mount Helper Service\nVersion 0.0\n\nNFS share mounted:\n" + res_mount + "\n", mimetype="text/plain")
        return response

    def on_status(self, request):
        cat_mounts_cp = subprocess.run(["cat", "/proc/mounts"], capture_output=True, text=True)
        res_mount = None
        for line in iter(cat_mounts_cp.stdout.splitlines()):
            sl = line.split(" ")
            if len(sl) > 3:
                if sl[1] == "/mnt/nfs_cam":
                    res_mount = sl[0]
        status = {
                "mounted": False
            }
        if res_mount is not None:
            status = {
                    "mounted": True,
                    "endpoint": res_mount
                }
        response = Response(json.dumps(status, indent=4), mimetype="application/json")
        return response

    def on_mount(self, request):
        response = self.authenticate_header(request)
        if response == True:
            response = Response("Error 400\nThis endpoint is POST only\n", mimetype="text/plain", status=400)
            if request.method == 'POST':
                if "resource" in request.form:
                    nfs_resource = request.form["resource"].strip()
                    nfs_resource = re.sub("[^A-Za-z0-9:\\./_-]+", "", nfs_resource)
                    umount_cp = subprocess.run(["umount", "/mnt/nfs_cam"], capture_output=True, text=True)
                    mount_cp = subprocess.run(["mount", "-t", "nfs", nfs_resource, "/mnt/nfs_cam"], capture_output=True, text=True)
                    cat_mounts_cp = subprocess.run(["cat", "/proc/mounts"], capture_output=True, text=True)
                    res_mount = None
                    for line in iter(cat_mounts_cp.stdout.splitlines()):
                        sl = line.split(" ")
                        if len(sl) > 3:
                            if sl[1] == "/mnt/nfs_cam":
                                res_mount = line
                    output = umount_cp.stdout + umount_cp.stderr + mount_cp.stdout + mount_cp.stderr
                    if res_mount is None:
                        response = Response("Mounting " + nfs_resource + " failed!\nOutput:\n" + output + "\n", mimetype="text/plain", status=500)
                    else:
                        response = Response("Mounting " + nfs_resource + " to /mnt/nfs_cam\nOutput:\n" + output + "\nResulting mount:\n" + res_mount + "\n", mimetype="text/plain", status=200)
                else:
                    response = Response("Error 400\nMissing NFS resource\n", mimetype="text/plain", status=400)
        return response

    def on_destroy(self, request):
        response = self.authenticate_header(request)
        if response == True:
            print("Recieved authenticated request to close the helper service")
            self.shutdown_server(request)
            response = Response("Sending SIGKILL\n", mimetype="text/plain", status=200)
        return response

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(redis_host='localhost'):
    app = HelperService()
    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple("0.0.0.0", 8082, app, use_debugger=True)
