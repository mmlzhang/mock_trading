import traceback

from flask import jsonify, Blueprint
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import LoginRequiredException, MessageContentException, ObjectException
from .utils.dingtalk import send_message, Header

# pylint: disable=unused-argument

error_blueprint = Blueprint('error_handler', __name__,)


@error_blueprint.app_errorhandler(404)
def handle_page_not_found(e):
    return jsonify({"msg": str(e), "code": 404}), 404


@error_blueprint.app_errorhandler(LoginRequiredException)
def handle_login_required(e):
    return jsonify({"msg": str(e), "code": 401}), 401


@error_blueprint.app_errorhandler(MessageContentException)
def handle_message_format(e):
    return jsonify({"msg": str(e), "code": 400}), 400


@error_blueprint.app_errorhandler(ObjectException)
def handle_object_exception(e):
    return jsonify({"msg": str(e), "code": 200}), 200


@error_blueprint.app_errorhandler(500)
def handle_server_exception(e):
    send_message(title="服务器内部异常", text=str(traceback.format_exc()), header_text=Header.Server)
    return jsonify({"error": "Internal server error", "code": 500}), 500


@error_blueprint.app_errorhandler(SQLAlchemyError)
def handle_sql_exception(e):
    send_message(title="数据库异常", text=str(e), header_text=Header.Server)
    return jsonify({"error": "Internal server error", "code": 500}), 500
