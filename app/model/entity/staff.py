import requests

from http import HTTPStatus
from sqlalchemy import Column, DateTime, event, Integer, String

from .entity_base import EntityBase
from .role import Role
from ..relation.staff_role import StaffRole
from ...cache import cache, EXPIRE_CACHE
from ...util import get_init_db
from app.model.db import merge, seq


class Staff(EntityBase):
    __tablename__ = 'staff'

    staff_id = Column(Integer, seq, primary_key=True)
    name = Column(String)
    surname = Column(String)
    bio = Column(String)
    contacts = Column(String, default='{"tel":null,"email":null,"tg":null,"fb":null,"vk":null,"insta":null}')
    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['staff_id', 'name', 'surname', 'bio', 'contacts',
                            'create_date', 'update_date', 'last_change_by_id']

    get_relations_map = {
        'roles': lambda staff_id: StaffRole.get_relation_ids_by_staff(staff_id)
    }

    update_fields = ['name', 'surname', 'bio', 'contacts', 'case_id', 'roles']

    update_simple_fields = ['name', 'surname', 'bio', 'contacts', 'last_change_by_id']

    update_relations_map = {
        'roles': lambda staff, roles: StaffRole.update_relations_by_staff(staff.staff_id, roles)
    }

    delete_relations_funcs = [
        StaffRole.delete_relations_by_staff
    ]

    @classmethod
    @cache.cache('get_staff_by_id', expire=EXPIRE_CACHE)
    def get_staff_by_id(cls, staff_id):
        return cls.query.filter_by(staff_id=staff_id).first()

    @classmethod
    @cache.cache('get_staff', expire=EXPIRE_CACHE)
    def get_staff(cls):
        return [staff.to_dict() for staff in cls.query.order_by(cls.staff_id).all()]

    @classmethod
    def create(cls, data):
        staff = None
        if 'staff_id' in data:
            staff = merge(cls.get_staff_by_id(data['staff_id']))

        if staff:
            return staff

        staff = cls(name=data['name'], surname=data['surname'], bio=data['bio'])
        staff.add()
        staff.last_change_by_id = data.get('last_change_by_id', staff.staff_id)

        staff.add()

        cls._invalidate_cache(staff)

        role_relations = StaffRole.create_relations_by_staff(staff.staff_id, data['roles'])
        if len(role_relations) == 0:
            staff.delete_self()
            cls._invalidate_cache(staff)
            return None

        return staff

    @classmethod
    def delete(cls, staff_id):
        staff = merge(cls.get_staff_by_id(staff_id))
        if staff:
            cls._delete(staff)
            return staff
        return None

    @classmethod
    def _invalidate_cache(cls, staff):
        cache.invalidate(cls.get_staff_by_id, 'get_staff_by_id', staff.staff_id)
        cache.invalidate(cls.get_staff, 'get_staff')


@event.listens_for(Staff.__table__, 'after_create')
def create_all(*args, **kwargs):
    admin_id = merge(Role.get_role_by_name('admin')).role_id
    admins_data = get_init_db()['admins']
    for admin_data in admins_data:
        admin_data['roles'] = [admin_id]
        Staff.create(admin_data)
