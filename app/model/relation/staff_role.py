from sqlalchemy import Column, Index, Integer

from .relation_base import RelationBase
from ...cache import cache, EXPIRE_CACHE
from app.model.db import merge, merge_list, seq


class StaffRole(RelationBase):
    __tablename__ = 'staff_role'

    id = Column(Integer, seq, primary_key=True)
    staff_id = Column(Integer)
    role_id = Column(Integer)

    idx = Index('idx_staff_role', id, staff_id, role_id)

    @classmethod
    @cache.cache('get_relation_staff_role', expire=EXPIRE_CACHE)
    def get_relation(cls, staff_id, role_id):
        return cls.query.filter_by(staff_id=staff_id, role_id=role_id).first()

    @classmethod
    @cache.cache('get_level_relation_staff_role', expire=EXPIRE_CACHE)
    def get_level_relation(cls, staff_id, role_level):
        from ..entity.role import Role

        return Role.query.filter_by(level=role_level).join(cls, Role.role_id == cls.role_id).\
            filter_by(staff_id=staff_id).first()

    @classmethod
    @cache.cache('get_relations_role_by_staff', expire=EXPIRE_CACHE)
    def get_relations_by_staff(cls, staff_id):
        return cls.query.filter_by(staff_id=staff_id).all()

    @classmethod
    def get_relation_ids_by_staff(cls, staff_id):
        return [rel.role_id for rel in merge_list(cls.get_relations_by_staff(staff_id))]

    @classmethod
    def __create_by_role(cls, staff_id, role):
        level_relation = merge(cls.get_level_relation(staff_id, role.level))
        relation = merge(cls.get_relation(staff_id, role.role_id))
        if relation is None and level_relation is None:
            relation = cls(staff_id=staff_id, role_id=role.role_id)
            relation.add()
            cache.invalidate(cls.get_relation, 'get_relation_staff_role', staff_id, role.role_id)
            cache.invalidate(cls.get_level_relation, 'get_level_relation_staff_role', staff_id, role.level)
            cache.invalidate(cls.get_relations_by_staff, 'get_relations_role_by_staff', staff_id)
        return relation

    @classmethod
    def create_by_id(cls, staff_id, role_id):
        from ..entity.role import Role

        role = merge(Role.get_role_by_id(role_id))
        if role:
            return cls.__create_by_role(staff_id, role)
        return None

    @classmethod
    def create_by_name(cls, staff_id, role_name):
        from ..entity.role import Role

        role = merge(Role.get_role_by_name(role_name.lower()))
        if role:
            return cls.__create_by_role(staff_id, role)
        return None

    @classmethod
    def create_relations_by_staff(cls, staff_id, role_ids):
        relations = []
        for role_id in role_ids:
            relation = cls.create_by_id(staff_id, role_id)
            if relation:
                relations.append(relation)
        return relations

    @classmethod
    def update_relations_by_staff(cls, staff_id, role_ids):
        from ..entity.role import Role

        relations = merge_list(cls.get_relations_by_staff(staff_id))
        relation_ids = cls.get_relation_ids_by_staff(staff_id)
        to_add_ids, to_delete_ids = cls._analyze_update(relation_ids, role_ids)
        if len(to_delete_ids) == len(relation_ids):
            exist = False
            for to_add_id in to_add_ids:
                if Role.get_role_by_id(to_add_id):
                    exist = True
                    break
            if not exist:
                return
        for relation in filter(lambda rel: rel.role_id in to_delete_ids, relations):
            cls.__delete_relation(relation)
        for to_add_id in to_add_ids:
            cls.create_by_id(staff_id, to_add_id)
        cache.invalidate(cls.get_relations_by_staff, 'get_relations_role_by_staff', staff_id)

    @classmethod
    def __delete_relation(cls, relation):
        from ..entity.role import Role

        relation.delete_self()
        role = merge(Role.get_role_by_id(relation.role_id))
        cache.invalidate(cls.get_relation, 'get_relation_staff_role', relation.staff_id, relation.role_id)
        cache.invalidate(cls.get_level_relation, 'get_level_relation_staff_role', relation.staff_id, role.level)

    @classmethod
    def delete_relations_by_staff(cls, staff_id):
        relations = merge_list(cls.get_relations_by_staff(staff_id))
        for relation in relations:
            cls.__delete_relation(relation)
        cache.invalidate(cls.get_relations_by_staff, 'get_relations_role_by_staff', staff_id)
