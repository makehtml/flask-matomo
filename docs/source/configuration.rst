Configuration
===============

Details about a route
---------------------

You can set details for a route, which will overwrite the parsed details.

.. code-block:: python

  @app.route("/users")
  @matomo.details(route="/users", action_name="Users")
  def all_users():
      return render_template("users.html")

Or passing the information to the `Matomo` constructor.

.. code-block:: python

  matomo = Matomo(
    ...,
    routes_details={"/users": {"action_name": "Users"}},
  )


Ignore routes
-------------

If you wan't to prevent one route from being tracked, you can ignore it by adding a decorator in front of the function.

.. code-block:: python

  @app.route("/admin")
  @matomo.ignore()
  def admin():
      return render_template("admin.html")

Or passing the information to the `Matomo` constructor.

.. code-block:: python

  matomo = Matomo(
    ...,
    ignored_routes=["/admin"],
  )

Ignore routes by patterns
-------------------------

You can also prevent all routes that match a pattern from being tracked, by giving the pattern(s) to the Matomo constructor.

.. code-block:: python

  matomo = Matomo(
    ...,
    ignored_patterns=["/.*admin.*"],
  )

Ignore tracking based on user-agent regex
-----------------------------------------

You can skip tracking requests made with specific user-agents.

.. code-block:: python

  matomo = Matomo(
    ...,
    ignored_ua_patterns=[".*bot.*"],
  )
