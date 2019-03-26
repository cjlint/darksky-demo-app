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
