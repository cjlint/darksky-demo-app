import os
import tempfile
import mock
import pytest
import requests
from cat_mood import main


# adapted from http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def client():
    app = main.create_app(os.path.realpath("tests/config.py"))
    with tempfile.TemporaryDirectory() as tmpdirname:
        app.config["CACHE_LOCATION"] = tmpdirname
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
