def show_stats(movies):

    total = len(movies)

    watched = sum(
        1
        for movie in movies
        if movie["watched"]
    )

    remaining = total - watched

    ratings = [
        movie["rating"]
        for movie in movies
        if movie["rating"] is not None
    ]

    average = (
        sum(ratings) / len(ratings)
        if ratings
        else 0
    )

    print("\n--- STATISTICS ---")

    print(f"Total movies: {total}")
    print(f"Watched: {watched}")
    print(f"Remaining: {remaining}")
    print(f"Average rating: {average:.1f}")