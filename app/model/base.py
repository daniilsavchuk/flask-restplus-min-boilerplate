from app.model.db import db


class Base(db.Model):
    __abstract__ = True

    def add(self):
        with db.auto_commit():
            db.session.add(self)

    def delete_self(self):
        with db.auto_commit():
            db.session.delete(self)
