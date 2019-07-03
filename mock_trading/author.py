
import json
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, g, request, Response, jsonify

from .dao import db
from .dao.models.vmatch import User, Fund, Order
from .constant import HEADER_TOKEN_NAME, REGISTER_TOKEN
from .exceptions import LoginRequiredException, MessageContentException
from .utils.dto_vmatch import OrderStatus
from .status_code import SUCCESS_CODE


user_blueprint = Blueprint('user', __name__)


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.cookies.get(HEADER_TOKEN_NAME)
        if token:
            user = User.verify_auth_token(token)
            g.user = user
            response = func(*args, **kwargs)
            if User.need_update_token(token):
                response.set_cookie(key=HEADER_TOKEN_NAME, value=user.generate_auth_token())
            return response
        raise LoginRequiredException("Login Required")
    return wrapper


@user_blueprint.route('/register', methods=["GET", "POST"])
def register():
    """注册, 暂时使用GET请求，没有前端页面，做简单的注册即可"""
    if request.method == "GET":
        return render_template("user/register.html")
    elif request.method == "POST":
        username = request.json.get("username").strip()
        password = request.json.get("password").strip()
        re_password = request.json.get("rePassword").strip()
        token = request.json.get("token").strip()
        if not username or not password or not re_password:
            raise MessageContentException("username and password is required!")
        if password != re_password:
            raise MessageContentException("password difference!")
        if token != REGISTER_TOKEN:
            return MessageContentException("token error!")
        user = User.query.filter(User.name == username).filter(User.is_active.is_(True)).first()
        if user:
            raise MessageContentException("user already exists!")
        user = User()
        user.name = username
        password = password
        user.set_md5_password(password)

        user.create_time = datetime.now()
        db.session.add(user)
        db.session.commit()
        db.session.flush()
        return jsonify(SUCCESS_CODE)
    raise MessageContentException("requests method error!")


@user_blueprint.route('/login', methods=["GET", "POST"])
def login():
    """登录"""
    if request.method == "GET":
        return render_template('user/login.html')
    elif request.method == "POST":
        username = request.json.get("username")
        password = request.json.get("password")
        if not username or not password or not isinstance(password, str) or not isinstance(username, str):
            raise MessageContentException("username and password are must string!")
        user = User.query.filter(User.name == username).\
            filter(User.password == User.verify_password(password)).first()
        if not user:
            raise MessageContentException("user doesn't exists!")
        data = json.dumps({'name': username, "code": 200})
        response = Response(data, content_type='application/json; charset=utf-8')
        response.set_cookie(key=HEADER_TOKEN_NAME, value=user.generate_auth_token())
        return response
    raise MessageContentException("request method error!")


@user_blueprint.route('/logout')
@login_required
def logout():
    """注销"""
    response = Response(json.dumps(SUCCESS_CODE), content_type='application/json; charset=utf-8')
    response.set_cookie(key=HEADER_TOKEN_NAME, value=g.user.generate_auth_token(key="log out"))
    return response


@user_blueprint.route('/api/user/info')
@login_required
def get_info():
    db.create_all()
    fund = db.session.query(Fund).filter(Fund.user_id == g.user.id).first()
    orders = db.session.query(Order).filter(Order.user_id == g.user.id).count()
    pending_orders = db.session.query(Order).filter(Order.user_id == g.user.id).\
        filter(Order.status == OrderStatus.pending).count()
    data = {
        "username": g.user.name,
        "fund": fund.amount if fund else 0,
        "orders": orders,
        "pendingOrders": pending_orders,
    }
    return jsonify(data)
