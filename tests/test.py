from flask import Flask, render_template, jsonify
from flask_matomo import *

app = Flask(__name__)
matomo = Matomo(app,
                matomo_url="https://matomo.mydomain.com",
                id_site=5,
                token_auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                secure=True,
                allowed_paths=None,
                custom_action_name_by_path=None)

@app.route("/")
def index():
    return jsonify(message='Hello!')

if __name__ == "__main__":
    app.run(debug=True, port=7777)