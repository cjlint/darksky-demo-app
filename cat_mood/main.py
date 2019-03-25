import sys
from datetime import timedelta
from flask import Flask, jsonify
from darkskyclient import DarkSkyClient


def create_app(config):
    app = Flask(__name__)
    # read config, create darksky client object
    app.config.from_pyfile(config, silent=True)
    darksky = DarkSkyClient(
        app.config["DARKSKY_KEY"],
        app.config.get("CACHE_LIFETIME", timedelta(days=3)),
        app.logger,
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
        # get_temp_and_moon might raise an error, in which case this endpoint will correctly return a 500 error
        return darksky.get_temp_and_moon(latitude, longitude, time)

    return app


if __name__ == "__main__":
    try:
        config = sys.argv[1]
    except:
        # default
        config = "config.py"
    app = create_app(config)
    app.run(host="0.0.0.0", debug=True)
