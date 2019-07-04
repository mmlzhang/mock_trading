# pylint: disable=broad-except

import requests
from flask import current_app

from big_vmatch import __version__


class Colors(object):

    WARNING = "#ec971f"
    INFO = "#449d44"
    ERROR = "#c9302c"


class Header(object):

    Server = "服务器内部异常"
    Work = "AdCreative work 脚本通知"


def send_message(title, text, header_text=None, color=Colors.ERROR):
    environ = current_app.config.get('APP_ENVIRONMENT', 'bigvmatch')
    title = '<font color={0} >{1}</font>'.format(color, title)
    message = """## {0}\n### {1}\n{2}\n{3}""".format(
        title, "{}  v{}".format(environ, __version__), '#### {0}'.format(header_text) if header_text else '', text)
    payload = {"msgtype": "markdown",
               "markdown": {"title": title, "text": message},
               "isAtAll": True}
    try:
        requests.post(current_app.config['DING_TALK_URL'], json=payload)
    except Exception as e:
        print(e)
