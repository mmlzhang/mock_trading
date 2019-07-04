
class LoginRequiredException(Exception):
    """ 必须登录 """


class MessageContentException(Exception):
    """ 格式 内容 错误"""


class ObjectException(Exception):
    """ 没有找到你要得到的信息 """
