import copy
import json
import time
import typing
from dataclasses import dataclass
from unittest import mock
from urllib.parse import parse_qs, urlsplit

import flask
import httpx
import pytest
from flask import Flask
from werkzeug import exceptions as werkzeug_exc
from werkzeug.wrappers import response

from flask_matomo2 import Matomo
from flask_matomo2.trackers import PerfMsTracker


@dataclass
class Response:
    status_code: int
    text: str = "text"


@pytest.fixture(name="matomo_client")
def fixture_matomo_client():
    client = mock.Mock(spec=httpx.Client)

    client.get = mock.Mock(return_value=Response(status_code=204))
    return client


@pytest.fixture(name="settings", scope="session")
def fixture_settings() -> dict:
    return {"idsite": 1, "base_url": "http://testserver", "token_auth": "FAKE_TOKEN"}


def create_app(matomo_client, settings: dict) -> Flask:
    app = Flask(__name__)

    app.config.update({"TESTING": True})
    matomo = Matomo(
        app,
        client=matomo_client,
        matomo_url="http://trackingserver",
        id_site=settings["idsite"],
        token_auth=settings["token_auth"],
        ignored_routes=["/health"],
        ignored_patterns=[".*/old.*"],
        ignored_ua_patterns=["creepy-bot.*"],
    )

    @app.route("/foo")
    def foo():
        return "foo"

    @app.route("/health")
    def health_fn():
        return "ok"

    @app.route("/heartbeat")
    @matomo.ignore()
    def heartbeat():
        return "ok"

    @app.route("/some/old/path")
    @app.route("/old/path")
    @app.route("/really/old")
    def old():
        return "old"

    @app.route("/set/custom/var")
    def custom_var():
        if "flask_matomo2" not in flask.g:
            flask.g.flask_matomo2 = {"tracking": True}
        # flask.g.flask_matomo2["custom_tracking_data"] = {
        #     "e_a": "Playing",
        #     "cvar": {"anything": "goes"},
        # }
        with PerfMsTracker(scope=flask.g.flask_matomo2, key="pf_srv"):
            flask.g.flask_matomo2["custom_tracking_data"] = {
                "e_a": "Playing",
                "cvar": {"anything": "goes"},
            }
            time.sleep(0.1)
        return "custom_var"

    @app.route("/bor")
    @matomo.details(action_name="Foo-Bor")
    def bor():
        return "foo-bor"

    @app.route("/bar")
    def bar():
        raise werkzeug_exc.InternalServerError()

    # async def baz(request):
    #     data = await request.json()
    #     return JSONResponse({"data": data})

    # app.add_route("/baz", baz, methods=["POST"])
    return app


@pytest.fixture(name="app")
def fixture_app(matomo_client, settings: dict) -> Flask:
    return create_app(matomo_client, settings)


@pytest.fixture(name="app_wo_token")
def fixture_app_wo_token(matomo_client, settings: dict) -> Flask:
    new_settings = copy.deepcopy(settings)
    new_settings["token_auth"] = None
    return create_app(matomo_client, new_settings)


@pytest.fixture(name="expected_q")
def fixture_expected_q(settings: dict) -> dict:
    return {
        "idsite": [str(settings["idsite"])],
        "url": ["http://testserver"],
        "apiv": ["1"],
        # "lang": ["None"]
        "rec": ["1"],
        # "ua": ["python-httpx/0.24.0"],
        "cip": ["127.0.0.1"],
        "token_auth": ["FAKE_TOKEN"],
        "send_image": ["0"],
        "cvar": ['{"http_status_code": 200, "http_method": "GET"}'],
    }


@pytest.fixture(name="client")
def fixture_client(app: Flask) -> typing.Generator[httpx.Client, None, None]:
    with httpx.Client(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(name="client_wo_token")
def fixture_client_wo_token(app_wo_token: Flask) -> typing.Generator[httpx.Client, None, None]:
    with httpx.Client(app=app_wo_token, base_url="http://testserver") as client:
        yield client


def assert_query_string(url: str, expected_q: dict) -> None:
    urlparts = urlsplit(url[6:-2])
    q = parse_qs(urlparts.query)
    assert q.pop("rand") is not None
    assert q.pop("gt_ms") is not None
    assert q.pop("ua")[0].startswith("python-httpx")
    cvar = q.pop("cvar")[0]
    expected_cvar = expected_q.pop("cvar")[0]
    if "pf_srv" in expected_q:
        expected_lower_limit = expected_q.pop("pf_srv")
        assert float(q.pop("pf_srv")[0]) >= expected_lower_limit

    assert q == expected_q
    assert json.loads(cvar) == json.loads(expected_cvar)


def test_matomo_client_gets_called_on_get_foo(client, matomo_client, expected_q: dict):
    response = client.get("/foo")
    assert response.status_code == 200

    matomo_client.get.assert_called()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
    assert_query_string(str(matomo_client.get.call_args), expected_q)


def test_matomo_client_is_not_called_when_user_agent_should_be_ignored(client, matomo_client):
    response = client.get("/foo", headers={"user-agent": "creepy-bot-with-suffix"})
    assert response.status_code == 200

    matomo_client.get.assert_not_called()


def test_middleware_works_without_token(client_wo_token, matomo_client, expected_q: dict):
    response = client_wo_token.get("/foo")
    assert response.status_code == 200

    matomo_client.get.assert_called()  # get.assert_called()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
    del expected_q["cip"]
    del expected_q["token_auth"]
    assert_query_string(str(matomo_client.get.call_args), expected_q)


def test_lang_gets_tracked_if_accept_language_is_set(client, matomo_client, expected_q: dict):
    response = client.get("/foo", headers={"accept-language": "sv"})
    assert response.status_code == 200

    matomo_client.get.assert_called()  # get.assert_called()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
    expected_q["lang"] = ["sv"]
    assert_query_string(str(matomo_client.get.call_args), expected_q)


def test_x_forwarded_for_changes_ip(client, matomo_client, expected_q: dict):
    forwarded_ip = "127.0.0.2"
    response = client.get("/foo", headers={"x-forwarded-for": forwarded_ip})
    assert response.status_code == 200

    matomo_client.get.assert_called()  # get.assert_called()

    expected_q["url"][0] += "/foo"
    expected_q["action_name"] = ["/foo"]
    expected_q["cip"] = [forwarded_ip]
    assert_query_string(str(matomo_client.get.call_args), expected_q)


def test_matomo_client_doesnt_gets_called_on_get_health(
    client: httpx.Client,
    matomo_client,
):
    response = client.get("/health")
    assert response.status_code == 200

    matomo_client.get.assert_not_called()


def test_matomo_client_doesnt_gets_called_on_get_heartbeat(
    client: httpx.Client,
    matomo_client,
):
    response = client.get("/heartbeat")
    assert response.status_code == 200

    matomo_client.get.assert_not_called()


def test_matomo_details_updates_action_name(client, matomo_client, expected_q: dict):
    response = client.get("/bor")
    assert response.status_code == 200

    matomo_client.get.assert_called()  # get.assert_called()

    expected_q["url"][0] += "/bor"
    expected_q["action_name"] = ["Foo-Bor"]
    assert_query_string(str(matomo_client.get.call_args), expected_q)


@pytest.mark.parametrize("path", ["/some/old/path", "/old/path", "/really/old"])
def test_matomo_client_doesnt_gets_called_on_get_old(
    client: httpx.Client, matomo_client, path: str
):
    response = client.get(path)
    assert response.status_code == 200

    matomo_client.get.assert_not_called()


def test_matomo_client_gets_called_on_get_custom_var(
    client: httpx.Client, matomo_client, expected_q: dict
):
    response = client.get("/set/custom/var")
    assert response.status_code == 200

    matomo_client.get.assert_called()

    expected_q["url"][0] += "/set/custom/var"
    expected_q["action_name"] = ["/set/custom/var"]
    expected_q["e_a"] = ["Playing"]
    expected_q["pf_srv"] = 90000
    expected_q["cvar"] = ['{"http_status_code": 200, "http_method": "GET", "anything": "goes"}']

    assert_query_string(str(matomo_client.get.call_args), expected_q)


def test_app_works_even_if_tracking_fails(client, matomo_client):
    matomo_client.get = mock.Mock(return_value=Response(status_code=500))
    response = client.get("/foo")

    assert response.status_code == 200

    matomo_client.get.assert_called()


def test_app_works_even_if_tracking_raises(client, matomo_client):
    matomo_client.get = mock.Mock(side_effect=httpx.HTTPError("custom"))
    response = client.get("/foo")

    assert response.status_code == 200

    matomo_client.get.assert_called()


def test_matomo_client_gets_called_on_get_bar(
    client: httpx.Client, matomo_client, expected_q: dict
):
    response = client.get("/bar")
    assert response.status_code >= 500

    matomo_client.get.assert_called()

    expected_q["url"][0] += "/bar"
    expected_q["action_name"] = ["/bar"]
    expected_q["cvar"][0] = expected_q["cvar"][0].replace("200", "500")

    assert_query_string(str(matomo_client.get.call_args), expected_q)
