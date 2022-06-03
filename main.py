from datetime import datetime, timedelta
from typing import List

from cinema import _encrypt_password
from configuration import config
from database_adapter import adapter
from database_population.imdb_util import *


def set_default_admin():
    base_admin_ = config['base_admin']
    if not adapter.select_admin(base_admin_['email']):
        print("Inserting default admin...")
        key, salt = _encrypt_password(str(base_admin_['password']))
        adapter.insert_new_user_tup((base_admin_['first_name'], base_admin_['last_name'],
                                     base_admin_['email'], key, base_admin_['phone_num'], 1, 0, False,
                                     True))
        adapter.insert_salt((base_admin_['email'], salt))


def set_default_user():
    base_user_ = config['base_user']
    if not adapter.select_user(base_user_['email']):
        print("Inserting default user...")
        key, salt = _encrypt_password(str(base_user_['password']))  # todo make sure that all calls to encrypt pw can
        # only pass strings
        adapter.insert_new_user_tup((base_user_['first_name'], base_user_['last_name'],
                                     base_user_['email'], key, base_user_['phone_num'], 0, 0, True,
                                     True))
        adapter.insert_salt((base_user_['email'], salt))


def _get_poster(movie_title):
    return {
        'Shaun of the Dead': 'https://m.media-amazon.com/images/M/MV5BMTg5Mjk2NDMtZTk0Ny00YTQ0LWIzYWEtMWI5MGQ0Mjg1OTNkXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg',
        'Star Trek First Contact': 'https://upload.wikimedia.org/wikipedia/en/0/01/Star_trek_first_contact_poster.jpg',
        'Twelve Monkeys': 'https://m.media-amazon.com/images/M/MV5BN2Y2OWU4MWMtNmIyMy00YzMyLWI0Y2ItMTcyZDc3MTdmZDU4XkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_.jpg',
        'Halloween Kills': 'https://m.media-amazon.com/images/M/MV5BM2RmMGY2Y2UtNjA1NS00NGE4LThiNzItMmE1NTk5NzI5NmE0XkEyXkFqcGdeQXVyNjY1MTg4Mzc@._V1_FMjpg_UX1000_.jpg',
        'The Last Samurai': 'https://m.media-amazon.com/images/M/MV5BMzkyNzQ1Mzc0NV5BMl5BanBnXkFtZTcwODg3MzUzMw@@._V1_.jpg',
        'Avatar': 'https://m.media-amazon.com/images/M/MV5BMTYwOTEwNjAzMl5BMl5BanBnXkFtZTcwODc5MTUwMw@@._V1_FMjpg_UX1000_.jpg',
        'Dances With Wolves': 'https://s3.amazonaws.com/static.rogerebert.com/uploads/movie/movie_poster/dances-with-wolves-1990/large_hpmclspug1I8EwKSWhL7pWWltA.jpg',
        'National Treasure': 'https://m.media-amazon.com/images/M/MV5BMTY3NTc4OTYxMF5BMl5BanBnXkFtZTcwMjk5NzUyMw@@._V1_.jpg',
        'Primer': 'https://m.media-amazon.com/images/I/512aPRrkErL._AC_.jpg',
        'No Time To Die': 'https://m.media-amazon.com/images/M/MV5BYWQ2NzQ1NjktMzNkNS00MGY1LTgwMmMtYTllYTI5YzNmMmE0XkEyXkFqcGdeQXVyMjM4NTM5NDY@._V1_FMjpg_UX1000_.jpg',
        'Inception': 'https://flxt.tmsimg.com/assets/p7825626_p_v10_af.jpg',
        "Zack Snyder's Justice League": 'https://upload.wikimedia.org/wikipedia/en/6/60/Zack_Snyder%27s_Justice_League.png',
        'The Prestige': 'https://m.media-amazon.com/images/M/MV5BMjA4NDI0MTIxNF5BMl5BanBnXkFtZTYwNTM0MzY2._V1_.jpg',
        'Jaws': 'https://images.moviesanywhere.com/246283329b6fbec9158c89d2c8a76bfe/3f2f72c0-6820-413f-a347-173d330d27ed.jpg',
        'Titanic': 'https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_.jpg',

    }[movie_title]


def populate_movies():
    imdb_functions = {'plot': get_plot, 'cast': get_cast, 'directors': get_directors,
                      'poster': _get_poster, 'producer': get_producer, 'reviews': get_reviews, 'trailer': get_trailer,
                      'category': get_category, 'runtime': get_runtime, 'mpaa': get_mpaa_rating,
                      'imdb': get_imdb_rating}
    movies_to_insert: List[tuple] = list()
    movie_titles = config['default_movies']
    for movie_title in movie_titles:
        try:
            movie = {key: func(movie_title) for key, func in imdb_functions.items()}
        except:
            print(f"Cannot collect information for {movie_title}")
            continue

        release_date = datetime.now().date() + timedelta(6 * 365 / 12) if random.randint(0,
                                                                                         1) else datetime.now().date()
        movie_tup = (movie_title, adapter.get_genre_id(movie['category']), movie['cast'], movie['directors'],
                     movie['producer'], movie['plot'], movie['imdb'], movie['runtime'], _get_poster(movie_title),
                     movie['trailer'],
                     adapter.get_mpaa_rating_id(movie['mpaa']), release_date)
        movies_to_insert.append(movie_tup)
    adapter.insert_movies(movies_to_insert)


if __name__ == '__main__':
    populate_movies()
    set_default_user()
    set_default_admin()

    adapter.setup()
