from enum import Enum
import requests
import requests_cache
from datetime import timedelta


# Would be more appropriate in another file if we wanted to introduce UncleIkesClient
class City(Enum):
    SEATTLE = ("47.6097", "-122.3331")
    NYC = ("40.7127", "-74.0059")


# DarkSkyClient class allows us to set secret_key once in constructor.
# It also sets an example for the creation of a companion class (UncleIkesClient)
# (python doesn't have interfaces like Go but they could still inherit from a common base class)
class DarkSkyClient:
    def __init__(
        self, secret_key, cache_backend=None, cache_location=None, logger=None
    ):
        self._secret_key = secret_key
        kwargs = {}
        # don't overwrite these defaults unless present
        if cache_backend:
            kwargs["backend"] = cache_backend
        if cache_location:
            kwargs["location"] = cache_location
        self._cache_session = requests_cache.CachedSession(**kwargs)
        self._logger = logger

    def get(self, latitude: float, longitude: float, time: int) -> (float, float):
        response = self._cache_session.get(
            f"https://api.darksky.net/forecast/{self._secret_key}/{latitude},{longitude},{time}",
            headers={"Accept-Encoding": "gzip"},
            # alerts data block is automatically omitted in Time Machine requests
            params={"exclude": ["minutely", "hourly"]},
        )
        if self._logger:
            self._logger.debug(response.text)
        if not response.ok:
            raise RuntimeError(
                f"{response.status} response from DarkSky: {response.text}"
            )
        try:
            # might error if 204 response, or response is not json for whatever reason
            json_result = response.json()
            temperature = json_result["currently"]["temperature"]
            moon_phase = json_result["daily"]["data"][0]["moonPhase"]
        except KeyError as e:
            raise RuntimeError(f"Unexpected json format from DarkSky", e, response.text)
        return (temperature, moon_phase)

    def get_city(self, city_name: str, time: int) -> (float, float):
        latitude, longitude = City[city_name.upper()].value
        return self.get(latitude, longitude, time)
