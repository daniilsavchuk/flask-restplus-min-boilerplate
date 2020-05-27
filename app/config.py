import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    ROOT = os.path.abspath(os.path.dirname(__file__))
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_boilerplate_main.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER_UI_DOC_EXPANSION = 'list'
    ERROR_404_HELP = False


class DevelopmentConfig(Config):
    DEV = True
    URL_PREFIX = '/api/v1'
    DOC_URL = '/swagger'


class ProductionConfig(Config):
    DEV = False
    URL_PREFIX = '/api/v1'
    DOC_URL = False



config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)
