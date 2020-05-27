import os

from flask import Blueprint, url_for
from flask_restplus import Api
from flask_restplus.apidoc import apidoc

from . import staff_controller
from . import default_controller

from ..util import get_version
from ..util.dto import RoleDto


class ApiScheme(Api):
    @property
    def specs_url(self):
        scheme = os.getenv('SCHEME', 'http')
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


def init_app(app):
    apidoc.url_prefix = app.config['URL_PREFIX']
    blueprint = Blueprint('api', __name__, url_prefix=app.config['URL_PREFIX'])
    api = ApiScheme(blueprint, version=get_version(), title='BP API', description='API for BP',
                    doc=app.config['DOC_URL'], security='token',
                    authorizations={
                        'token': {
                            'type': 'apiKey',
                            'in': 'header',
                            'name': 'authorization'
                        }
                    })

    api.add_namespace(default_controller.api, path='/')
    api.add_namespace(RoleDto.api, path='/role')
    api.add_namespace(staff_controller.api, path='/staff')

    app.register_blueprint(blueprint)
