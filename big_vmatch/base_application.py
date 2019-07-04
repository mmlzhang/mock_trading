
from flask import Flask
from flask_compress import Compress
from flask_cors import CORS

from .dao import db
from .constant import STATIC_DIR, TEMPLATES_DIR
from .settings import get_config


def create_app(env):
    """ 创建app,注册配置 """

    application = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)
    CORS(application, supports_credentials=True)
    compress = Compress()

    application.config.from_object(get_config(env))

    from .author import user_blueprint
    application.register_blueprint(user_blueprint)

    from .views import main_blueprint
    application.register_blueprint(main_blueprint)

    from .error_handler import error_blueprint
    application.register_blueprint(error_blueprint)

    from .fund import fund_blueprint
    application.register_blueprint(fund_blueprint)

    from .quotation import quotation_blueprint
    application.register_blueprint(quotation_blueprint)

    compress.init_app(application)
    db.init_app(application)

    return application
