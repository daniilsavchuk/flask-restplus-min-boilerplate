from flask import current_app
from flask_restplus import Resource

from ..cache import invalidate_all_cache

from ..model.entity.role import Role
from ..model.entity.staff import Staff

from ..model.db import merge, db
from ..util import all_in, get_version, get_test_data
from ..util.dto import DefaultDto


api = DefaultDto.api


@api.route('version')
class VersionApi(Resource):
    @api.doc('get_version')
    @api.response(200, 'Success', DefaultDto.version)
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    def get(self):
        """Get number of version"""
        return {'version': get_version()}


def _fill_test_data():
    test_data = get_test_data()
    last_change_by_id = Staff.get_staff()[0]['staff_id']


    if 'staff' in test_data:
        for staff_data in test_data['staff']:
            if all_in(['runet_id', 'name', 'surname', 'bio', 'roles'], staff_data):
                roles = [merge(Role.get_role_by_name(role_name.lower())).role_id for role_name in staff_data['roles']
                         if Role.get_role_by_name(role_name)]

                if len(roles) > 0:
                    staff_data['roles'] = roles
                    staff_data['last_change_by_id'] = last_change_by_id
                    Staff.create(staff_data)


_reset_parser = api.parser()
_reset_parser.add_argument('fill', type=str, help='Is the database needs to be filled by test data.',
                           location='args', choices=['true', 'false'], default='false')


@api.route('db/reset')
class DatabaseResetApi(Resource):
    @api.doc('reset_database')
    @api.expect(_reset_parser)
    @api.response(204, 'Database Reset Successful')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    def post(self):
        """Reset the database"""
        args = _reset_parser.parse_args()
        db.session.remove()
        db.drop_all(app=current_app)
        invalidate_all_cache()
        db.create_all(app=current_app)
        if args['fill'] == 'true':
            _fill_test_data()
        return '', 204
