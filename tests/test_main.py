import os
import tempfile
import mock
import pytest
import requests
from cat_mood import main


# This is an actual DarkSky key, obviously there is no billing attached.
#
# This is obviously not ideal, because it means our tests rely on whether or not darksky is up,
# and it means we need to stay under 1000 requests per day when testing.
#
# A better way to test a "real" api call would be to make a mock darksky api with whatever
# features we need, and test against that instead.
#
# However, this is super easy for now
DARKSKY_KEY = "8e18f2297c727554623f3b6cca64358b"

# adapted from http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def client():
    with tempfile.TemporaryDirectory() as tmpdirname:
        app = main.create_app(DARKSKY_KEY, location=tmpdirname)
        app.config["TESTING"] = True
        client = app.test_client()
        yield client


def test_get_index(client):
    assert client.get("/").data.startswith(b"<html>")


def test_get_data(client):
    assert client.get("/data/42.3601,-71.0589,155357669").get_json() == {
        "temperature": 37.21,
        "moon": 0.64,
    }


# TODO couldn't figure this out, keep getting error:
# TypeError: get() missing 1 required positional argument: 'url'
# even though it seems like it should be fine
#
# def test_cache_hit(client):
#    with mock.patch(
#        "requests.sessions.Session.get", wraps=requests.sessions.Session.get
#    ) as real_get_mock:
#        assert client.get("/data/42.3601,-71.0589,155357669").ok
#        assert client.get("/data/42.3601,-71.0589,155357669").ok
#        real_get_mock.assert_called_once()


# TODO should test error conditions, especially validating the comma-separated format
