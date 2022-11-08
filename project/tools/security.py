import base64
import calendar
import datetime
import hashlib
import hmac

import jwt
from flask import current_app

from project.config import ALGORITHM, JWT_SECRET


def __generate_password_digest(password: str) -> bytes:
    return hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=current_app.config["PWD_HASH_SALT"],
        iterations=current_app.config["PWD_HASH_ITERATIONS"],
    )


def generate_password_hash(password: str) -> str:
    return base64.b64encode(__generate_password_digest(password)).decode('utf-8')


def compare_passwords(password_hash, other_password) -> bool:
    hash_digest = generate_password_hash(other_password)
    return hmac.compare_digest(password_hash, hash_digest)


def generate_password_hash(password: str) -> str:
    return base64.b64encode(__generate_password_digest(password)).decode('utf-8')


def compose_passwords(password_hash, other_password):
    return password_hash == generate_password_hash(other_password)


def generate_tokens(email, password, password_hash=None, is_refresh=False):
    if email is None:
        return None

    if not is_refresh:
        if not compose_passwords(other_password=password, password_hash=password_hash):
            return None

    data = {
        "email": email,
        "password": password,
    }

    min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    data["exp"] = calendar.timegm(min30.timetuple())
    access_token = jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)

    days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
    data["exp"] = calendar.timegm(days130.timetuple())
    refresh_token = jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)

    return {"access_token": access_token,
            "refresh_token": refresh_token}


def approve_refresh_token(refresh_token):
    data = jwt.decode(jwt=refresh_token, key=JWT_SECRET, algorithms=ALGORITHM)
    username = data.get("email")
    return generate_tokens(username, None, is_refresh=True)


def get_data_from_token(refresh_token):
    try:
        data = jwt.decode(jwt=refresh_token, key=JWT_SECRET,
                          algorithms=ALGORITHM)
        return data
    except Exception:
        return None
