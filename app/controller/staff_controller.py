from collections import OrderedDict
from flask_restplus import Resource
from http import HTTPStatus

from ..model.entity.role import Role
from ..model.entity.staff import Staff

from ..util import  get_items_related_to_page
from ..util.dto import StaffDto

from app.model.db import merge_list


api = StaffDto.api

_list_parser = api.parser()
_list_parser.add_argument('page_id', type=int, help='The page identifier.', location='args', default=0)
_list_parser.add_argument('page_size', type=int, help='The page size. -1 means all staff.', location='args', default=-1)

_item_parser = api.parser()
_item_parser.add_argument('staff_id', type=int, help='The staff identifier.', location='args', required=True)


@api.route('')
class StaffApi(Resource):
    @api.doc('list_staff')
    @api.expect(_list_parser)
    @api.response(200, 'Success', StaffDto.staff_list)
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    def get(self):
        """List all staff"""
        args = _list_parser.parse_args()
        all_staff = Staff.get_staff()
        count = len(all_staff)
        staff = get_items_related_to_page(*args.values(), all_staff, Staff)
        roles = OrderedDict([(r['role_id'], r) for r in Role.get_roles()])
        return OrderedDict([('roles', roles), ('staff', staff), ('count', count)])

    @api.doc('create_staff')
    @api.expect(StaffDto.staff, validate=True)
    @api.response(201, 'Staff created', StaffDto.staff)
    @api.response(400, 'Missing staff parameters')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    def post(self):
        """Create a new staff"""
        staff = Staff.create(api.payload)
        if staff:
            result = staff.to_dict()
            result.update(Staff.get_relations(staff.staff_id))
            return result, 201
        api.abort(HTTPStatus.BAD_REQUEST, 'Missing correct roles')


    @api.doc('delete_staff')
    @api.expect(_item_parser)
    @api.response(204, 'Staff deleted')
    @api.response(400, 'Missing staff identifier')
    @api.response(401, 'Unauthorized')
    @api.response(403, 'Forbidden operation')
    @api.response(404, 'Staff not found')
    def delete(self):
        """Delete an existing staff"""
        args = _item_parser.parse_args()
        if Staff.delete(args['staff_id']):
            return '', 204
        api.abort(HTTPStatus.NOT_FOUND, "Staff {args['staff_id']} not found")