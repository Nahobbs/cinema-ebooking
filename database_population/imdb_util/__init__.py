import random
from cachetools import TTLCache, cached
from youtubesearchpython import VideosSearch
from imdb import IMDb

imdb = IMDb()
cache = TTLCache(maxsize=100, ttl=86400)


class NotFound(Exception):
    pass


@cached(cache)
def _get_movie(movie_title: str):
    results = imdb.search_movie(movie_title)[0]
    imdb.get_movie_infoset()
    return imdb.get_movie(results.movieID)


@cached(cache)
def get_top_250():
    res = imdb.get_top250_movies()
    movies = [movie['title'] for movie in res]
    return movies


def get_plot(movie_title: str):
    results = _get_movie(movie_title)
    results = str(results['plot'][0])
    try:
        results = results.split('::')[0]  # remove unnecessary characters
    except ValueError:
        pass
    return results


def get_poster(movie_title: str):
    movie = _get_movie(movie_title)
    return movie['cover url']


def get_directors(movie_title: str):
    movie = _get_movie(movie_title)
    res = str()
    for person in movie['directors']:
        res = res + person['name'] + ", "
    if len(movie['directors']) == 1:
        for person in movie['directors']:
            res = res + person['name']
    return res


def get_runtime(movie_title: str):
    movie = _get_movie(movie_title)
    runtime_mins = int(movie['runtimes'][0])
    runtime = '{:02d}:{:02d}'.format(*divmod(runtime_mins, 60))
    hours, minutes = runtime.split(':')
    runtime = int(hours) * 60 + int(minutes)
    return runtime


def get_cast(movie_title: str):
    movie = _get_movie(movie_title)
    res = str()
    for person in movie['cast']:
        res = res + person['name'] + ", "
    return res


def get_category(movie_title: str):
    movie = _get_movie(movie_title)
    return movie['genres'][0]


def get_producer(movie_title: str):
    movie = _get_movie(movie_title)
    res = str()
    # added this hackish nonsense cause VARCHAR count for producer in movie is not large enough
    person_count = 0
    for person in movie['producers']:
        if person_count == 1:
            break
        res = res + person['name']
        person_count += 1
    return res


def get_reviews(movie_title: str):
    movie = _get_movie(movie_title)
    results = imdb.get_movie_reviews(movie.movieID)
    # select a random review from the 10000000 provided lol
    return results['data']['reviews'][random.randint(0, len(results['data']['reviews']) - 1)]['content']


def get_imdb_rating(movie_title: str):
    movie = _get_movie(movie_title)
    return movie['rating']


def get_trailer(movie_title: str):
    vid = VideosSearch(f"{movie_title} Movie Trailer", limit=1)
    return vid.result()['result'][0]['link']


def get_mpaa_rating(movie_title: str):
    movie = _get_movie(movie_title)
    for cert in movie['certificates']:
        # grab the USA film rating
        if 'United States' in str(cert):
            # make sure it's not the TV rating
            if 'TV' in str(cert):
                continue
            return str(cert).split(':')[1]
