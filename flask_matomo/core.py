import requests

from flask import current_app, request
from threading import Thread
import re

from . import MatomoError

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Matomo(object):
    """The Matomo object provides the central interface for interacting with Matomo.

    Args:
        app (Flask object): created with Flask(__name__)
        matomo_url (str): url to Matomo installation
        id_site (int): id of the site that should be tracked on Matomo
        token_auth (str): token that can be found in the area API in the settings of Matomo
        base_url (str): url to the site that should be tracked
        secure (boolean): verification of trusted certificates
        allowed_paths (str): allowed paths of every incoming request to be tracked, use regex sintax. Ex: 'dasd|paht1|admin'
        custom_action_name_by_path (dict): dictionary of custom action_name indentified by path witch is used for match referenced request.path
    """

    def __init__(self, app=None, matomo_url=None, id_site=None, token_auth=None, base_url=None, secure=True, allowed_paths=None, custom_action_name_by_path=None):
        self.app = app
        self.matomo_url = matomo_url
        self.id_site = id_site
        self.token_auth = token_auth
        self.base_url = base_url.strip("/") if base_url else base_url
        self.secure = secure
        self.ignored_routes = []
        self.allowed_paths = allowed_paths
        self.routes_details = {}
        self.custom_action_name_by_path = custom_action_name_by_path

        if not matomo_url:
            raise ValueError("matomo_url has to be set")
        if type(id_site) != int:
            raise ValueError("id_site has to be an integer")
        if type(secure) != bool:
            raise ValueError('secure has to be a bool')
        if allowed_paths and type(allowed_paths) != str:
            raise ValueError('allowed_paths has to be a string, ex: "path1|pahtz|etc|admin"')
        if custom_action_name_by_path and type(custom_action_name_by_path) != dict:
            raise ValueError("custom_action_name_by_path has to be a dict, ex: {'path': 'custom name for it'}")
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize app"""
        app.before_request(self.before_request)

    def before_request(self):
        """Exectued before every request, parses details about request"""
        # Don't track track request, if user used ignore() decorator for route
        if request.endpoint in self.ignored_routes:
            return

        # Don't track request, if path is now allowed
        if self.allowed_paths and not self.is_allowed_path():
            return

        if self.base_url:
            url = self.base_url + request.path
        else:
            url = request.url

        if request.endpoint:
            action_name = request.endpoint
        else:
            action_name = "Not Found"

        user_agent = request.user_agent
        ip_address = request.remote_addr

        keyword_arguments = {
            "action_name": action_name,
            "url": url,
            "user_agent": user_agent,
            "ip_address": ip_address
        }

        # Overwrite action_name, if it was configured with config()
        if self.routes_details.get(action_name) and self.routes_details.get(action_name).get("action_name"):
            keyword_arguments["action_name"] = self.routes_details.get(
                action_name).get("action_name")

        # Set custom actiom name by path
        if self.custom_action_name_by_path:
            action_name = self.set_custom_action_name()
            if action_name:
                keyword_arguments["action_name"] = action_name

        # Create new thread with request, because otherwise the original request will be blocked
        Thread(target=self.track, kwargs=keyword_arguments).start()

    def track(self, action_name, url, user_agent=None, id=None, ip_address=None):
        """Send request to Matomo

        Args:
            action_name (str): name of the site
            url (str): url to track
            user_agent (str): User-Agent of request
            id (str): id of user
            ip_address (str): ip address of request
        """
        data = {
            "idsite": str(self.id_site),
            "rec": "1",
            "ua": user_agent,
            "action_name": action_name,
            "url": url,
            "_id": id,
            "token_auth": self.token_auth,
            "cip": ip_address
        }

        r = requests.post(self.matomo_url + "/piwik.php", params=data, verify=self.secure)

        if r.status_code != 200:
            raise MatomoError('Status code: {code} - Response: {response_text}'.format(
                code=r.status_code,
                response_text=r.text
                )
            )

    def ignore(self):
        """Ignore a route and don't track it

        Args:
            action_name (str): name of the site
            url (str): url to track
            user_agent (str): User-Agent of request
            id (str): id of user
            ip_address (str): ip address of request

        Examples:
            @app.route("/admin")
            @matomo.ignore()
            def admin():
                return render_template("admin.html")
        """
        def wrap(f):
            self.ignored_routes.append(f.__name__)
            return f

        return wrap

    def details(self, action_name=None):
        """Set details like action_name for a route

        Args:
            action_name (str): name of the site

        Examples:
            @app.route("/users")
            @matomo.details(action_name="Users")
            def all_users():
                return render_template("users.html")
        """
        def wrap(f):
            self.routes_details[f.__name__] = {
                "action_name": action_name
            }
            return f

        return wrap

    def is_allowed_path(self):
        """Check using regex if the path is allowed

            self.allowed_paths (str): 'path1|pathz|etc'
        """
        if re.search(self.allowed_paths, request.path):
            return True
        else:
            return False

    def set_custom_action_name(self):
        """ Return custom action_name if request.path contain any element of custom_action_name_by_path

            self.custom_action_name_by_path (dict) : {'path': 'custom name for it'}
        """
        for p in self.custom_action_name_by_path:
            if p in request.path:
                return self.custom_action_name_by_path[p]