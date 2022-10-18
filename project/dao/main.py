from sqlalchemy import desc
from sqlalchemy.orm import scoped_session
from werkzeug.exceptions import NotFound

from project.dao.base import BaseDAO
from project.models import Genre, Director, Movie, User
from project.tools.security import generate_password_hash


class GenresDAO(BaseDAO[Genre]):
    __model__ = Genre


class DirectorsDAO(BaseDAO[Director]):
    __model__ = Director



class MoviesDAO(BaseDAO[Movie]):
    __model__ = Movie

    def get_one(self, bid):
        return self.session.query(Movie).get(bid)

    def get_all(self):
        return self.session.query(Movie).all()

    def get_all_order_by(self, page, filter):
        stmt = self._db_session.query(self.__model__)
        if filter:
            stmt = stmt.order_by(desc(self.__model__.year))
        if page:
            try:
                return stmt.paginate(page, self._items_per_page).items
            except NotFound:
                return []
        return stmt.all()

class UserDAO(BaseDAO[User]):
    __model__ = User

    def __init__(self, db_session: scoped_session):
        super().__init__(db_session)
        self.db = None

    def create(self, login, password):
        try:
            self._db_session.add(
                User(
                    email=login,
                    password=generate_password_hash(password)
                )
            )
            self._db_session.commit()
            print('Пользователь добавлен')
        except Exception as e:
            print(e)
            self._db_session.rollback()

    def get_user_by_login(self, login):
        try:
            stmt = self._db_session.query(self.__model__).filter(self.__model__.email == login).one()
            return stmt
        except Exception as e:
            print(e)
            return {}

    def update(self, login, data):
        try:
            self._db_session.query(self.__model__).filter(self.__model__.email == login).update(data)
            self._db_session.commit()
            print('Пользователь обновлен')
        except Exception as e:
            print(e)
            self._db_session.rollback()
