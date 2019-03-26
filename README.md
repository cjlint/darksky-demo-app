# Cat Mood Prediction

This project houses a small web app where you can query temperature and moon phase data using [Dark Sky API](https://darksky.net/poweredby/). This data is specifically very important for predicting cat moods, hence the name!

Requires Python 3 (See `Implementation Comments > Python`)
Frontend web page works best on Google Chrome (datetime picker has convenient default selection tool on Chrome)

## Build

```bash
brew install python # (if python3 not installed)
pip install --user pipenv
pipenv sync --dev
pipenv run python setup.py sdist # produces tarball in dist directory
```

Running tests:

```bash
pipenv run python -m pytest
```

requests_cache library produces an ugly DeprecationWarning, oh well...

## Running the Server

Assuming your Dark Sky secret key is in `DARKSKY_KEY`:

```bash
pip install cat_mood-0.1.0.tar.gz
cat-mood-service ${DARKSKY_KEY}
```

## Usage for Data Scientists

Data scientists have two options: import the `DarkSkyClient` class and use it directly, or make requests against a running instance of the cat_mood app.

### Option 1 -- Direct usage

Install:

```bash
pip install cat_mood-0.1.0.tar.gz
```

Example usage:

```python
from datetime import datetime
from cat_mood.darkskyclient import DarkSkyClient

my_api_key = "abc123..."
client = DarkSkyClient(my_api_key)
epoch_time = int(datetime.now().timestamp())

client.get_city("Seattle", epoch_time)
# returns dictionary:
# {
#   "temperature": 45.0,
#   "moon": 0.95
# }
```

Allows data scientists to use the API without connecting to a running app, but means there will be less cache hits because they are maintaining their own cache rather than using the shared cache of the app instance.

### Option 2 -- Calling a running instance

```bash
curl http://running-cat-mood-instance:5000/data/47.6097,-122.3331,123456789
# returns json:
# {
#   "temperature": 45.0,
#   "moon": 0.95
# }
```

Requires data scientists to have access to a running instance, but means there will be more cache hits because they are using a shared cache between everyone calling the instance.

## Implementation Comments

### Python

I chose Python because I am familiar with it, and I'm familiar with the Flask framework. I was tempted to learn Go for this project, but I think python is a good choice here anyway because python is probably the best language to hand to a data scientist.

I don't know if Drift uses python2 or python3 -- I stuck with python3 here but there are libraries like [six](http://docs.python-requests.org/en/master/) that help you write code compatible with python 2 and 3.

### Vue.js

Vue is a small library that helps build reactive web UIs. I hadn't used Vue before but I chose it here because I was really happy with how small and simple it is, definitely a great tool for prototyping purposes (and potentially larger projects, I only scratched the surface).

### Caching

Dark Sky API charges for each request in excess of 1000 per day. To reduce costs, and to increase responsiveness, we cache results from Dark Sky API for 1 hour. This is the duration that Dark Sky specifies in its cache-control header, presumably because weather forecasts change and at some point you do need to grab more up-to-date data.

I used a library called [requests_cache](https://github.com/reclosedev/requests-cache) -- it is a companion to [requests](http://docs.python-requests.org/en/master/) that replaces the default `requests.Session` class and caches responses in a format of our choosing. We can chose how long the cache lasts, although it's probably best to stick to the 1 hour expiration. Responses are cached in a sqlite database by default.

Another solution would be [CacheControl](https://cachecontrol.readthedocs.io/en/latest/). the upsides are that it actually reads the cache-control header so we aren't obligated to manually set a reasonable cache lifetime, however it doesn't support sqlite out of the box (as far as I could tell).

#### More Caching

If we want to be sure we are conserving as many API calls as possible, there are more things we can cache. For example, we can maintain a LRU cache for API calls that ask for a time that has already happened -- weather forecasts from the past aren't going to change. LRU would mean we don't arbitrary bloat our cache size, and it also means we will always have the most common past times cached. This would be a great improvement, if data scientists ever want to know past forecasts at all.

Another thing we could do is request more information from Dark Sky with each call. By default, Dark Sky returns an hourly forecast for the entire day when you request a forecast. We could cache these results as well and use them to estimate a temperature/moon reading for other requests from the same day. However this adds complexity and it adds to uncached response times, since there is a lot more data coming over the wire, so I disabled this extra hourly information for now.
