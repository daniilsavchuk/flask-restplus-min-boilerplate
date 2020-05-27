from flask_restplus import fields, Namespace


class DefaultDto:
    api = Namespace('default', description='Default operations')
    version = api.model('version', {
        'version': fields.String(required=True, description='The number of version')
    })


class RoleDto:
    api = Namespace('role', description='Role operations')
    role = api.model('role', {
        'role_id': fields.Integer(required=True, description='The role unique identifier'),
        'name': fields.String(required=True, description='The role name'),
        'level': fields.Integer(required=True, description='The role level')
    })
    role_list = api.model('role_list', {
        'role_id': fields.Nested(role, required=True, description='The map role by role identifier')
    })


class StaffDto:
    api = Namespace('staff', description='Staff operations')
    # input for create
    staff = api.model('staff_in', {
        'id': fields.Integer(required=True, description='The staff RUNET ID'),
        'name': fields.String(required=True, description='The staff name'),
        'surname': fields.String(required=True, description='The staff surname'),
        'bio': fields.String(required=True, description='The staff biography'),
        'contacts': fields.String(description='The staff contacts'),
        'roles': fields.List(fields.Integer, required=True, description='The staff roles identifiers')
    })

    staff_list = api.model('staff_list', {
        'roles': fields.Nested(RoleDto.role_list, required=True, description='The list of roles'),
        'staff': fields.List(fields.Nested(staff), required=True, description='The list of staff'),
        'count': fields.Integer(required=True, description='The count of staff')
    })
