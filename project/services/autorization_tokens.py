import calendar
import datetime

import jwt
from flask import abort

from project.config import ALGORITHM, JWT_SECRET
from project.services import UsersService


class AuthService:
    def __init__(self, user_service: UsersService):
        self.user_service = user_service

    def generate_tokens(self, login, password, is_refresh=False):
        user = self.user_service.get_user_by_login(login)
        if user is None:
            raise abort(404)

        if not is_refresh:
            if not self.user_service.compare_passwords(user.password, password):
                abort(400)

        data = {
            "email": user.email,
            "password": user.password
        }

        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        data["exp"] = calendar.timegm(min30.timetuple())
        access_token = jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)

        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)

        return {"access_token": access_token,
                "refresh_token": refresh_token}

    def approve_refresh_token(self, refresh_token):
        data = jwt.decode(jwt=refresh_token, key=JWT_SECRET, algorithms=ALGORITHM)
        email = data.get("email")
        return self.generate_tokens(email, None, is_refresh=True)
