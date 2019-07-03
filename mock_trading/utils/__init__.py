
import hashlib
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.orm import class_mapper

from ..constant import DATE_FORMAT, DAY_FORMAT, PASSWORD_SALT1, PASSWORD_SALT2


def is_open(now_time=datetime.now()):
    """
    股市是否开市
    Args:
        now_time: datetime

    Returns: bool

    """
    morning_open = datetime.strptime(str(datetime.now().date()) + ' 9:30:00', '%Y-%m-%d %H:%M:%S')
    morning_close = datetime.strptime(str(datetime.now().date()) + ' 11:30:00', '%Y-%m-%d %H:%M:%S')
    noon_open = datetime.strptime(str(datetime.now().date()) + ' 13:00:00', '%Y-%m-%d %H:%M:%S')
    noon_close = datetime.strptime(str(datetime.now().date()) + ' 15:30:00', '%Y-%m-%d %H:%M:%S')
    if (morning_open <= now_time <= morning_close) or (noon_open <= now_time <= noon_close):
        return True
    return False


def underline_to_camel(underline_format: str):
    """str下划线改驼峰命名"""
    if not isinstance(underline_format, str):
        raise TypeError("must be str")
    camel_format = ''.join([_s_.capitalize() for _s_ in underline_format.split('_')])
    return camel_format[:1].lower() + camel_format[1:]


def md5_password(password) -> str:
    """
    得到加密过后的md5值
    Args:
        password: str

    Returns: str

    """

    hash_md5 = hashlib.md5('{0}{1}.!'.format(PASSWORD_SALT1, password).encode('utf-8'))
    hash_md5.update('{0}{1}='.format(PASSWORD_SALT2, password).encode('utf-8'))
    return hash_md5.hexdigest()


def sqlalchemy_object_to_dict(model, ignore_list=None, is_camel=True) -> dict:
    """

    Args:
        model: sqlalchemy
        ignore_list: list
        is_camel: bool
    Returns:

    """
    def format_time(value):
        if type(value) is datetime:
            return value.strftime(DATE_FORMAT)
        elif type(value) is date:
            return value.strftime(DAY_FORMAT)
        elif type(value) is Decimal:
            return float(value.quantize(Decimal('0.00000')))
        return value
    ignore_list = [] if ignore_list is None else [x.property.key for x in ignore_list]
    columns = [c.key for c in class_mapper(model.__class__).columns if c.key not in ignore_list]
    return dict((underline_to_camel(c) if is_camel else c, format_time(getattr(model, c))) for c in columns)
