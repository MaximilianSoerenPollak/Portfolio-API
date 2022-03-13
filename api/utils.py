from passlib.context import CryptContext
from sqlalchemy import inspect


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_pw, hashed_pw):
    return pwd_context.verify(plain_pw, hashed_pw)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
