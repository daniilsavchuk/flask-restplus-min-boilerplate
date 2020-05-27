from collections import OrderedDict
from datetime import datetime, time
from dateutil import parser

from ...util import any_in, datetime_to_str, validate_iso8601
from app.model.base import Base
from app.model.db import merge


class EntityBase(Base):
    __abstract__ = True

    serialize_items_list = []
    get_relations_map = {}

    update_fields = []
    update_simple_fields = []
    update_relations_map = {}

    delete_relations_funcs = []

    @classmethod
    def now(cls):
        return datetime.now()

    def to_dict(self, items=None):
        def dictionate_entity(entity):
            if isinstance(entity, datetime):
                return datetime_to_str(entity)
            elif isinstance(entity, time):
                return entity.strftime('%H:%M')
            elif 'to_dict' in dir(entity):
                return entity.to_dict()
            else:
                return entity

        return OrderedDict([(key, dictionate_entity(getattr(self, key)))
                           for key in (self.serialize_items_list if items is None else items)])

    @classmethod
    def from_dict(cls, data):
        item = cls()
        for field in cls.__table__.columns.keys():
            if field in data:
                if cls.__table__.columns[field].type.python_type == time:
                    if validate_iso8601(data[field]):
                        setattr(item, field, parser.parse(data[field]).time())
                elif cls.__table__.columns[field].type.python_type == datetime:
                    if validate_iso8601(data[field]):
                        setattr(item, field, parser.parse(data[field]))
                else:
                    setattr(item, field, data[field])
        return merge(item)

    @classmethod
    def get_relations(cls, item_id, items=None):
        result = OrderedDict([(cls.__table__.columns.keys()[0], item_id)])
        for key, func in cls.get_relations_map.items():
            if items is None or key in items:
                result.update({key: func(item_id)})
        return result

    @classmethod
    def _is_update_fields(cls, data):
        return any_in(cls.update_fields, data)

    def _update_simple_fields(self, data):
        for field in self.update_simple_fields:
            if field in data:
                if self.__table__.columns[field].type.python_type == time:
                    if validate_iso8601(data[field]):
                        setattr(self, field, parser.parse(data[field]).time())
                elif self.__table__.columns[field].type.python_type == datetime:
                    if validate_iso8601(data[field]):
                        setattr(self, field, parser.parse(data[field]))
                else:
                    setattr(self, field, data[field])
        self.add()

    def _update_relations(self, data):
        for key, func in self.update_relations_map.items():
            if key in data:
                func(self, data[key])

    @classmethod
    def _delete(cls, item):
        item.delete_self()
        item_id = getattr(item, cls.__table__.columns.keys()[0])
        for delete_func in cls.delete_relations_funcs:
            delete_func(item_id)
        cls._invalidate_cache(item)

    @classmethod
    def _invalidate_cache(cls, item):
        pass
