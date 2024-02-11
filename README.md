# flask-matomo2

![](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)
[![PyPI](https://img.shields.io/pypi/v/flask-matomo2.svg?style=flat-square&colorB=dfb317)](https://pypi.org/project/flask-matomo2/)
 [![Docs](https://img.shields.io/badge/docs-readthedocs-red.svg?style=flat-square)](https://flask-matomo2.readthedocs.io)

flask-matomo2 is a library which lets you track the requests of your Flask website using Matomo (Piwik).

Forked from [LucasHild/flask-matomo](https://github.com/LucasHild/flask-matomo).

## Installation

```
pip install flask-matomo2
```

## Using flask-matomo2 in your project

Simply add `flask-matomo2` to your dependencies:

```toml
# pyproject.toml
dependencies = [
  "flask-matomo2",
]

```
### Using Poetry

```bash
poetry add flask-matomo2
```

### Using PDM

```bash
pdm add flask-matomo2
```

## Usage

```python
from flask import Flask, jsonify
from flask_matomo2 import Matomo

app = Flask(__name__)
matomo = Matomo(app, matomo_url="https://matomo.mydomain.com",
                id_site=5, token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

@app.route("/")
def index():
  return jsonify({"page": "index"})

if __name__ == "__main__":
  app.run()
```

In the code above:

1. The *Matomo* object is created by passing in the Flask application and arguments to configure Matomo.
2. The *matomo_url* parameter is the url to your Matomo installation.
3. The *id_site* parameter is the id of your site. This is used if you track several websites with one Matomo installation. It can be found if you open your Matomo dashboard, change to site you want to track and look for &idSite= in the url.
4. The *token_auth* parameter can be found in the area API in the settings of Matomo. It is required for tracking the ip address.


### Adding details to route

You can provide details to a route in 2 ways, first by using the `matomo.details` decorator:

```python
from flask import Flask, jsonify
from flask_matomo2 import Matomo

app = Flask(__name__)
matomo = Matomo(app, matomo_url="https://matomo.mydomain.com",
                id_site=5, token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

@app.route("/foo")
@matomo.details(action_name="Foo")
def foo():
  return jsonify({"page": "foo"})

if __name__ == "__main__":
  app.run()
```

or by giving details to the Matomo constructor:
```python
from flask import Flask, jsonify
from flask_matomo2 import Matomo

app = Flask(__name__)
matomo = Matomo(
  app,
  matomo_url="https://matomo.mydomain.com",
  id_site=5,
  token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  routes_details={
    "/foo": {
      "action_name": "Foo"
    }
  }
)

@app.route("/foo")
def foo():
  return jsonify({"page": "foo"})

if __name__ == "__main__":
  app.run()
```

## Meta

Lucas Hild - [https://lucas-hild.de](https://lucas.hild.de)
This project is licensed under the MIT License - see the LICENSE file for details

# Release Notes

## Latest Changes

* build(deps-dev): update ruff requirement from 0.0.267 to 0.0.270. PR [#35](https://github.com/spraakbanken/flask-matomo2/pull/35) by [@dependabot[bot]](https://github.com/apps/dependabot).
* fix: allow for dont tracking based on user-agent. PR [#34](https://github.com/spraakbanken/flask-matomo2/pull/34) by [@kod-kristoff](https://github.com/kod-kristoff).
## 0.3.0 - 2023-05-25

### Added

- Add PerfMsTracker. PR [#33](https://github.com/spraakbanken/flask-matomo2/pull/33) by [@kod-kristoff](https://github.com/kod-kristoff).

## 0.2.0 - 2023-05-22
### Changed

- Track original IP address if request was forwarded by proxy. [Tanikai/flask-matomo](https://github.com/Tanikai/flask-matomo) by [@Tanakai](https://github.com/Tanakai).
- Change ignored routes to compare against rules instead of endpoint. [MSU-Libraries/flask-matomo](https://github.com/MSU-Libraries/flask-matomo) by [@meganschanz](https://github.com/meganschanz).
- Add ignored UserAgent prefix; set action to be url_rule. [MSU-Libraries/flask-matomo](https://github.com/MSU-Libraries/flask-matomo) by [@natecollins](https://github.com/natecollins).
- Fix matomo.ignore decorator.
- Handle request even if tracking fails. PR [#30](https://github.com/spraakbanken/flask-matomo2/pull/30) by [@kod-kristoff](https://github.com/kod-kristoff).
- Ignore routes by regex. PR [#29](https://github.com/spraakbanken/flask-matomo2/pull/29) by [@kod-kristoff](https://github.com/kod-kristoff).
- Make token_auth optional. PR [#28](https://github.com/spraakbanken/flask-matomo2/pull/28) by [@kod-kristoff](https://github.com/kod-kristoff).
- Track dynamic request data. PR [#27](https://github.com/spraakbanken/flask-matomo2/pull/27) by [@kod-kristoff](https://github.com/kod-kristoff).
- Also track request time. PR [#26](https://github.com/spraakbanken/flask-matomo2/pull/26) by [@kod-kristoff](https://github.com/kod-kristoff).
- Extend tracked variables. PR [#25](https://github.com/spraakbanken/flask-matomo2/pull/25) by [@kod-kristoff](https://github.com/kod-kristoff).
- fix matomo.details decorator. PR [#19](https://github.com/spraakbanken/flask-matomo2/pull/19) by [@kod-kristoff](https://github.com/kod-kristoff).


## 0.1.0

- Forked from [LucasHild/flask-matomo](https://github.com/LucasHild/flask-matomo).
- Renamed to `flask-matomo2`.
- Add test suite.
- Setup CI with Github Actions.
