from app.model.base import Base


class RelationBase(Base):
    __abstract__ = True

    @classmethod
    def _analyze_update(cls, old_ids, new_ids):
        old_ids = set(old_ids)
        new_ids = set(new_ids)
        to_add_ids = new_ids.difference(old_ids)
        to_delete_ids = old_ids.difference(new_ids)
        return to_add_ids, to_delete_ids
