from sqlalchemy.orm import DeclarativeBase

from db.meta import meta


class Base(DeclarativeBase):
    metadata = meta
