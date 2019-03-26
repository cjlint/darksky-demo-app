import os
import tempfile
import mock
import pytest
import requests
from cat_mood import main


# This test file makes 1 actual call to DarkSky API per test run
#
# Testing against the production DarkSky API is not super ideal, because it means our tests rely on
# whether or not darksky is up, and it means we need to stay under 1000 requests per day when testing.
# However it is still valuable as an integration test.
#
# A better way to test a "real" api call would be to make a mock darksky api with whatever
# features we need, and test against that instead.
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


def test_get_bad_params_float(client):
    resp = client.get("/data/a,b,c")
    assert resp.status_code == 400
    assert resp.get_json() == {
        "error": "Invalid arguments: a,b,c Reason: could not convert string to float: 'a'"
    }


def test_get_bad_params_int(client):
    resp = client.get("/data/12.0000,13.0000,midnight")
    assert resp.status_code == 400
    assert resp.get_json() == {
        "error": "Invalid arguments: 12.0000,13.0000,midnight Reason: invalid literal for int() with base 10: 'midnight'"
    }


def test_bad_params_not_enough_commas(client):
    resp = client.get("/data/12.0000by13.0000,midnight")
    assert resp.status_code == 400
    assert resp.get_json() == {
        "error": "Invalid arguments: 12.0000by13.0000,123456789 Reason: not enough values to unpack (expected 3, got 2)"
    }


def test_bad_params_too_many_commas(client):
    resp = client.get("/data/12.0000,13.0000,123456789,oclock")
    assert resp.status_code == 400
    assert resp.get_json() == {
        "error": "Invalid arguments: 12.0000,13.0000,123456789,oclock Reason: too many values to unpack (expected 3)"
    }


# TODO couldn't figure this out, keep getting error:
# TypeError: get() missing 1 required positional argument: 'url'
# even though it seems like it should be fine
#
# I _should_ have a test that makes sure the caching works, because that is an important part of business logic.
# But it proved difficult to correctly mock the request while keeping the functionality of requests_cache unchanged.
# At the end of the day it's semi-ok because we can trust that requests_cache has its own tests and we don't need
# to retest their implementation.
#
# def test_cache_hit(client):
#    with mock.patch(
#        "requests.sessions.Session.get", wraps=requests.sessions.Session.get
#    ) as real_get_mock:
#        assert client.get("/data/42.3601,-71.0589,155357669").ok
#        assert client.get("/data/42.3601,-71.0589,155357669").ok
#        real_get_mock.assert_called_once()
