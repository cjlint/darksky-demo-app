import sys
import argparse
from datetime import timedelta
from flask import Flask, jsonify
from cat_mood.darkskyclient import DarkSkyClient

# TODO error handler so that 500 errors appear as json, not html (not a huge issue for demo project)


def create_app(key, backend=None, location=None):
    app = Flask(__name__)
    # read config, create darksky client object
    darksky = DarkSkyClient(
        key, cache_backend=backend, cache_location=location, logger=app.logger
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
            response.status_code = 400
            return response
        temperature, moon = darksky.get(latitude, longitude, time)
        return jsonify({"temperature": temperature, "moon": moon})

    return app


def main():
    parser = argparse.ArgumentParser(description="Start a cat-mood instance")
    parser.add_argument("darksky_key", help="Secret key for darksky api")
    parser.add_argument(
        "--cache-backend",
        dest="backend",
        default=None,
        choices=["sqlite", "memory", "redis", "mongodb"],
        help="Backend caching strategy",
    )
    parser.add_argument(
        "--cache-location",
        dest="location",
        default="/tmp/cache",
        help="Location to store cache data",
    )
    args = parser.parse_args()

    app = create_app(args.darksky_key, args.backend, args.location)
    app.run(host="0.0.0.0", debug=True)


if __name__ == "__main__":
    main()
