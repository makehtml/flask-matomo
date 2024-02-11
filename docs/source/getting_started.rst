Getting Started
===============

Installation
------------

To install flask-matomo2::

  pip install flask-matomo2

Simple integration
------------------

.. code-block:: python

  from flask import Flask, jsonify
  from flask_matomo2 import *

  app = Flask(__name__)
  matomo = Matomo(
    app,
    matomo_url="https://matomo.mydomain.com",
    id_site=5,
    token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", # Optional
    ignore_routes=["/ignore/this/path"], # Optional, can be set with the ignore decorator
    routes_details={"/foo": {"action_name": "FOO"}}, # Optional, can be set with the details decorator
    ignored_patterns=[".*/html.*"], # Optional
  )

  @app.route("/")
  def index():
    return jsonify(route="/")

  @app.route("/ignore/this/path")
  def ignore_this_path():
    return jsonify(route="/ignore/this/path")

  @app.route("/ignore/this/path/also")
  @matomo.ignore()
  def ignore_this_path():
    return jsonify(route="/ignore/this/path/also")

  @app.route("/foo")
  def foo():
    return jsonify(route="/foo")

  @app.route("/foo2")
  @matomo.details(route="/foo2", action_name="FOO/2")
  def _foo2():
    return jsonify(route="/foo2")

  @app.route("/html/path")
  @app.route("/some/html/path")
  @app.route("/some/path.html")
  def html_content():
    return "<html>Prefer tracking html with Matomo JS tracking</html>"

  if __name__ == "__main__":
    app.run()

In the code above:

#. The ``Matomo`` object is created by passing in the Flask application and arguments to configure Matomo.
#. The ``matomo_url`` parameter is the url to your Matomo installation.
#. The ``id_site`` parameter is the id of your site. This is used if you track several websites with on Matomo installation. It can be found if you open your Matomo dashboard, change to site you want to track and look for ``&idSite=`` in the url.
#. The ``token_auth`` parameter can be found in the area API in the settings of Matomo. It is required for tracking the ip address, so if skipping this will skip tracking ip-addresses.
#. The route `/ignore/this/path` is ignored by the call to the Matomo constructor.
#. The route `/ignore/this/path/also` is ignored by using the ``ignore`` decorator.
#. The route `/foo` will be tracked with `action_name=FOO` by the call to the Matomo constructor.
#. The route `/foo2` will be tracked with `action_name=FOO/2` by using the ``details``, note the needed explicit naming of the route name if the function name doesn't match the route name.
#. The routes `/html/path`, `/some/html/path` and `/some/path.html` will be ignored because they match a `ignored_pattern`.


