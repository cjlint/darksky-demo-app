import mock
from cat_mood.darkskyclient import DarkSkyClient, City
from example_responses import good_data


# helper function to mock requests calls
# adapted from this gist https://gist.github.com/evansde77/45467f5a7af84d2a2d34f3fcb357449c
def mock_response(status=200, text=None, json_data=None, raise_for_status=None):
    mock_resp = mock.Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and text content
    mock_resp.status_code = status
    mock_resp.text = text
    # add json data if provided
    if json_data:
        mock_resp.text = str(json_data)
        mock_resp.json = mock.Mock(return_value=json_data)
    return mock_resp


@mock.patch("requests.sessions.Session.get")
def test_get(mock_get):
    mock_get.return_value = mock_response(json_data=good_data)
    assert DarkSkyClient("abc123", cache_backend="memory").get(
        123, -123, 123456789
    ) == (37.21, 0.64)


@mock.patch("requests.sessions.Session.get")
def test_get_seattle(mock_get):
    mock_get.return_value = mock_response(json_data=good_data)
    client = DarkSkyClient("abc123", cache_backend="memory")
    client.get_city("Seattle", 1234)
    mock_get.assert_called_with(
        "https://api.darksky.net/forecast/abc123/47.6097,-122.3331,1234",
        headers={"Accept-Encoding": "gzip"},
        params={"exclude": ["minutely", "hourly"]},
    )


@mock.patch("requests.sessions.Session.get")
def test_get_nyc(mock_get):
    mock_get.return_value = mock_response(json_data=good_data)
    client = DarkSkyClient("abc123", cache_backend="memory")
    client.get_city("Nyc", 1234)
    mock_get.assert_called_with(
        "https://api.darksky.net/forecast/abc123/40.7127,-74.0059,1234",
        headers={"Accept-Encoding": "gzip"},
        params={"exclude": ["minutely", "hourly"]},
    )


def test_city_enum_behavior():
    # this is a brittle test but I wanted to ensure I was using enums correctly
    assert City.SEATTLE.value == ("47.6097", "-122.3331")
    assert City.NYC.value == ("40.7127", "-74.0059")
    assert City["SEATTLE"] == City.SEATTLE
    assert City["NYC"] == City.NYC
