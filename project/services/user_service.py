import base64
import hashlib
import hmac
from typing import Optional

from flask import current_app
from flask_restx import abort

from project.dao import UserDAO
from project.exceptions import ItemNotFound
from project.models import User
from project.tools.security import generate_password_hash, generate_tokens, approve_refresh_token, get_data_from_token


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

    def update_token(self, refresh_token):
        return approve_refresh_token(refresh_token)

    def check(self, login, password):
        user = self.get_user_by_login(login)
        return generate_tokens(email=user.email, password=password, password_hash=user.password)

    def get_user_by_token(self, refresh_token):
        data = get_data_from_token(refresh_token)
        if data:
            return self.get_user_by_login(data.get('email'))

    def update_user(self, data, refresh_token):
        user = self.get_user_by_token(refresh_token)
        if user:
            self.dao.update(login=user.email, data=data)
            return self.get_user_by_token(refresh_token)

    def update_password(self, data, refresh_token):
        user = self.get_user_by_token(refresh_token)
        if not self.compare_passwords(password=data.get('old_password'), password_hash=user.password):
            raise abort(400)
        if user:
            self.dao.update(login=user.email, data={"password": generate_password_hash(data.get('new_password'))})
            return self.check(login=user.email, password=data.get('new_password'))

    def compare_passwords(self, password, password_hash) -> bool:
        decoded_digest = base64.b64decode(password_hash)
        hash_digest = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password.encode("utf-8"),
            salt=current_app.config["PWD_HASH_SALT"],
            iterations=current_app.config["PWD_HASH_ITERATIONS"],
        )

        return hmac.compare_digest(decoded_digest, hash_digest)
