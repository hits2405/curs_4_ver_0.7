from flask_restx import fields, Model

from project.setup.api import api

genre: Model = api.model('Жанр', {
    'id': fields.Integer(required=True, example=1),
    'name': fields.String(required=True, max_length=100, example='Комедия'),
})

director: Model = api.model('Режиссер', {
    'id': fields.Integer(required=True, example=1),
    'name': fields.String(required=True, max_length=100, example='Гайдай')
})

movie: Model = api.model('Фильм', {
    'id': fields.Integer(required=True, example=1),
    'title': fields.String(required=True, max_length=100, example='Бриллиантовая рука'),
    'description': fields.String(required=True, max_length=250, example='История про контрабандистов'),
    'trailer': fields.String(required=True, max_length=100, example='https://www.youtube.com/watch?v=UKei_d0cbP4'),
    'year' : fields.Integer(required=True, example=1970),
    'rating': fields.Float(required=True, example=9.9),
    'genre': fields.Nested(genre),
    'director': fields.Nested(director),
})


user: Model = api.model('Пользователь', {
    'id': fields.Integer(required=True, example=1),
    'email': fields.String(required=True, max_length=100, example='jon@gmail.com'),
    'password': fields.String(required=True, max_length=100, example='qwerty'),
    'name': fields.String(required=True, max_length=100, example='Jonh'),
    'surname': fields.String(required=True, max_length=100, example='Lenon'),
    'genre': fields.Nested(genre),
})