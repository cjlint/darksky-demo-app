import sys
from datetime import timedelta
from flask import Flask, jsonify
from cat_mood.darkskyclient import DarkSkyClient


def create_app(config):
    app = Flask(__name__)
    # read config, create darksky client object
    app.config.from_pyfile(config)
    darksky = DarkSkyClient(
        app.config["DARKSKY_KEY"],
        cache_backend=app.config.get("CACHE_BACKEND"),
        cache_location=app.config.get("CACHE_LOCATION"),
        logger=app.logger,
    )

    @app.route("/")
    def index():
        # serve index.html as a true static file, not a template
        # (to avoid confusion between Vue template and Jinja template)
        return app.send_static_file("index.html")

    @app.route("/data/<parameters>")
    def get_data(parameters):
        try:
            # Path param mimics darksky's api. Should be 3 values comma separated
            latitude, longitude, time = parameters.split(",", 3)
            latitude = float(latitude)
            longitude = float(longitude)
            time = int(time)
        except ValueError as e:
            msg = f"Invalid arguments: {parameters} Reason: {e}"
            app.logger.error(msg)
            response = jsonify({"error": msg})
            response.status_code = 422
            return response
        temperature, moon = darksky.get(latitude, longitude, time)
        return jsonify({"temperature": temperature, "moon": moon})

    return app


if __name__ == "__main__":
    try:
        config = sys.argv[1]
    except:
        # default
        config = "config.py"
    app = create_app(config)
    app.run(host="0.0.0.0", debug=True)
