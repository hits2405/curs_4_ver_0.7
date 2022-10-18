from .genres import api as genres_ns
from .director import api as director_ns
from .movie import api as movie_ns

__all__ = [
    'genres_ns',
    'director_ns',
    'movie_ns'
]
