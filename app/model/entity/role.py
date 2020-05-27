from sqlalchemy import Column, event, func, Integer, String

from .entity_base import EntityBase
from ...cache import cache, EXPIRE_CACHE
from ...util import get_init_db
from app.model.db import seq


class Role(EntityBase):
    __tablename__ = 'role'

    role_id = Column(Integer, seq, primary_key=True)
    name = Column(String)
    level = Column(Integer)

    serialize_items_list = ['role_id', 'name', 'level']

    @classmethod
    @cache.cache('get_role_by_id', expire=EXPIRE_CACHE)
    def get_role_by_id(cls, role_id):
        return cls.query.filter_by(role_id=role_id).first()

    @classmethod
    @cache.cache('get_role_by_name', expire=EXPIRE_CACHE)
    def get_role_by_name(cls, role_name):
        return cls.query.filter(func.lower(cls.name) == role_name).first()

    @classmethod
    @cache.cache('get_roles_by_level', expire=EXPIRE_CACHE)
    def get_roles_by_level(cls, role_level):
        return [_.to_dict() for _ in cls.query.filter_by(level=role_level).order_by(cls.role_id).all()]

    @classmethod
    @cache.cache('get_roles', expire=EXPIRE_CACHE)
    def get_roles(cls):
        return [_.to_dict() for _ in cls.query.order_by(cls.role_id).all()]


@event.listens_for(Role.__table__, 'after_create')
def create_all(*args, **kwargs):
    roles = get_init_db()['roles']
    for role in roles:
        Role(name=role['name'], level=role['level']).add()
