import requests
import requests_cache
from datetime import timedelta


# DarkSkyClient class allows us to set secret_key once in constructor
# Also sets an example for the creation of a companion class: UncleIkesClient
class DarkSkyClient:
    def __init__(self, secret_key, cache_lifetime, logger):
        self._cache_session = requests_cache.CachedSession(
            backend="sqlite", expire_after=cache_lifetime
        )
        self._secret_key = secret_key
        self._logger = logger

    def get_temp_and_moon(
        self, latitude: float, longitude: float, time: int
    ) -> (float, float):
        response = self._cache_session.get(
            f"https://api.darksky.net/forecast/{self._secret_key}/{latitude},{longitude},{time}",
            headers={"Accept-Encoding": "gzip"},
            # alerts data block is automatically omitted in Time Machine requests
            params={"exclude": ["minutely", "hourly"]},
        )
        if not response.ok:
            self._logger.error(
                f"{response.code} response from DarkSky: {response.text}"
            )
            response.raise_for_status()
        # might error if 204 response, or response is not json for whatever reason
        json_result = response.json()
        self._logger.debug(f"{latitude}, {longitude}, {time} ==> {json_result}")
        try:
            temperature = json_result["currently"]["temperature"]
            moon_phase = json_result["daily"]["moonPhase"]
        except KeyError as e:
            msg = "Unexpected json format from DarkSky"
            self._logger.error(msg, e)
            raise RuntimeError(msg, e)
        return (temperature, moon_phase)
