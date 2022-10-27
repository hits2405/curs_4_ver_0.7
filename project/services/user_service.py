import calendar
import datetime
from typing import Optional

import jwt
from flask_restx import abort

from project.dao import UserDAO
from project.exceptions import ItemNotFound
from project.models import User
from project.tools import security
from project.tools.security import generate_password_hash

secret = '249y823r9v8238r9u'
algo = 'HS256'





class UsersService:
    def __init__(self, dao: UserDAO) -> None:
        self.dao = dao

    def get_item(self, pk: int) -> User:
        if user := self.dao.get_by_id(pk):
            return user
        raise ItemNotFound(f'user with pk={pk} not exists.')

    def get_all(self, page: Optional[int] = None) -> list[User]:
        return self.dao.get_all(page=page)

    def get_user_by_login(self, login):
        return self.dao.get_user_by_login(login)

    def create_user(self, login, password):
        return self.dao.create(login, password)

    def generate_tokens(self, login, password, is_refresh=True):
        user = self.get_user_by_login(login)
        if user is None:
            raise abort(404)

        if not is_refresh:
            if not security.compare_passwords(user.password, is_refresh):
                raise abort(400)

        data = {
            "email": login,
            "password": password
        }

        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        data["exp"] = calendar.timegm(min30.timetuple())
        access_token = jwt.encode(data, secret, algorithm=algo)

        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(data, secret, algorithm=algo)

        tokens = {"access_token": access_token, "refresh_token": refresh_token}

        return tokens, 201

    def approve_refresh_token(self, refresh_token):
        data = jwt.decode(jwt=refresh_token, key=secret, algorithms=[algo])
        login = data.get('email')

        return self.generate_tokens(login, None, is_refresh=True)

    def check(self, login, password):
        user = self.get_user_by_login(login)
        return self.generate_tokens(login=user.email, password=password)


    def get_user_by_token(self, refresh_token):
        data = jwt.decode(jwt=refresh_token, key=secret, algorithms=[algo])
        if data:
            return self.get_user_by_login(data.get('email'))

    def update_user(self, data, refresh_token):
        user = self.get_user_by_token(refresh_token)
        if user:
            self.dao.update(login=user.email, data=data)
            return self.get_user_by_token(refresh_token)

    def update_password(self, data, refresh_token):
        user = self.get_user_by_token(refresh_token)
        if not security.compare_passwords(password=data.get('old_password'), password_hash=user.password):
            raise abort(400)
        if user:
            self.dao.update(login=user.email, data={"password": generate_password_hash(data.get('new_password'))})
            return self.check(login=user.email, password=data.get('new_password'))
