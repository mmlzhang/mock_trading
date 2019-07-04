
from datetime import datetime

from flask import current_app
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature)

from ...exceptions import LoginRequiredException

from .. import db
from ...constant import TOKEN_EXPIRATION_TIME, DATE_FORMAT, TOKEN_CREATE_TIME
from ...utils import sqlalchemy_object_to_dict, md5_password


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    password = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, default=True)
    create_time = db.Column(db.DateTime)

    def to_dict(self, ignore_list=None, is_camel=True):
        default_ignore = [User.password, User.id, User.is_active, User.create_time]
        ignore_list = ignore_list if ignore_list is not None else default_ignore
        return sqlalchemy_object_to_dict(self, ignore_list, is_camel)

    def set_md5_password(self, password):
        self.password = md5_password(password)

    @staticmethod
    def verify_password(password):
        return md5_password(password)

    def generate_auth_token(self, key=None):
        secret_key = key if key else current_app.config['SECRET_KEY']
        s = Serializer(secret_key, expires_in=TOKEN_EXPIRATION_TIME)
        return s.dumps({'id': self.id, TOKEN_CREATE_TIME: datetime.utcnow().strftime(DATE_FORMAT)})

    def generate_reset_password_token(self):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=24 * 60 * 60)
        return s.dumps({"group": self.group, 'email': self.email,
                        TOKEN_CREATE_TIME: datetime.utcnow().strftime(DATE_FORMAT)}).decode('utf-8')

    @staticmethod
    def need_update_token(token):
        """
        验证token剩余过期时间 是否是小于过期时间的一半。
        Args:
            token: str

        Returns:
            result: bool
        """
        try:
            data = User.get_data_from_token(token)
            create_token_time = datetime.strptime(data[TOKEN_CREATE_TIME], DATE_FORMAT)
            now_time = datetime.utcnow()
            if (now_time.timestamp() - create_token_time.timestamp()) > TOKEN_EXPIRATION_TIME / 2:
                return True
        except ValueError:
            raise LoginRequiredException("Login Required")
        return False

    @staticmethod
    def get_data_from_token(token):
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except SignatureExpired:
            raise LoginRequiredException("Login Required")    # valid token, but expired
        except BadSignature:
            raise LoginRequiredException("Login Required")    # invalid token
        return data

    @staticmethod
    def verify_auth_token(token):
        data = User.get_data_from_token(token)
        user = User.query.filter(User.id == data.get('id')).filter(User.is_active.is_(True)).first()
        if not user:
            raise LoginRequiredException("Login Required")
        return user


class Fund(db.Model):

    __tablename__ = 'fund'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    freeze = db.Column(db.Integer)
    # update_time = db.Column(db.DateTime)

    def to_dict(self, ignore_list=None, is_camel=True):
        return sqlalchemy_object_to_dict(self, ignore_list, is_camel)


class Order(db.Model):

    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    category = db.Column(db.String(64))
    status = db.Column(db.String(64))
    instrument_id = db.Column(db.String(64))
    count = db.Column(db.Integer)
    price = db.Column(db.Integer)  # 单位： 分
    total = db.Column(db.Integer)  # 单位： 分
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)

    def to_dict(self, ignore_list=None, is_camel=True):
        return sqlalchemy_object_to_dict(self, ignore_list, is_camel)


class UserStock(db.Model):

    __tablename__ = 'user_stock'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    instrument_id = db.Column(db.String(64))
    count = db.Column(db.Integer)
    freeze = db.Column(db.Boolean, default=False)  # 股票或者债券
    price = db.Column(db.Integer)  # 单位： 分
    create_time = db.Column(db.DateTime)

    def to_dict(self, ignore_list=None, is_camel=True):
        return sqlalchemy_object_to_dict(self, ignore_list, is_camel)
