import json
import os

from dateutil import parser
from dateutil.tz import tzlocal

from ..cache import cache, EXPIRE_CACHE


@cache.cache('get_version', expire=EXPIRE_CACHE)
def get_version():
    with open('VERSION') as version_file:
        version = version_file.read()
    return version.strip()


@cache.cache('get_init_db', expire=5)
def get_init_db():
    with open(os.path.join('app', 'model', 'init_db.json'), encoding='utf-8') as init_db_file:
        init_db = json.load(init_db_file)
    return init_db

def get_test_data():
    with open(os.path.join('app', 'model', 'test_data.json'), encoding='utf-8') as test_data_file:
        test_data = json.load(test_data_file)
    return test_data

def all_in(params, data):
    return all([p in data for p in params])


def any_in(params, data):
    return any([p in data for p in params])


def datetime_to_str(dt):
    return dt.replace(microsecond=0, tzinfo=tzlocal()).isoformat()


def validate_iso8601(str_val):
    try:
        parser.parse(str_val)
        return True
    except:
        pass
    return False


def get_page_params(page_id, page_size, count):
    if page_size == -1:
        return 0, count
    else:
        return max(page_id * page_size, 0), max((page_id + 1) * page_size, 0)


def get_items_related_to_page(page_id, page_size, all_items, cls):
    count = len(all_items)
    start, end = get_page_params(page_id, page_size, count)
    items = []
    for item in all_items[start:end]:
        result = item.copy()
        result.update(cls.get_relations(item[cls.__table__.columns.keys()[0]]))
        items.append(result)
    return items