from contextlib import contextmanager
from flask_sqlalchemy import SQLAlchemy as SQLAlchemy_
from sqlalchemy import Sequence


class SQLAlchemy(SQLAlchemy_):
    @contextmanager
    def auto_commit(self, throw=True):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            if throw:
                raise e


db = SQLAlchemy()
seq = Sequence('bp_seq')


def merge(item):
    if item:
        return db.session.merge(item)
    return None


def merge_list(item_list):
    return [merge(item) for item in item_list]
