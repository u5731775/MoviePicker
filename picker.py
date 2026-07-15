import random


def pick_random_movie(movies):

    unwatched = [
        movie
        for movie in movies
        if not movie["watched"]
    ]

    if not unwatched:
        return None

    return random.choice(unwatched)