
import os


class BaseConfig(object):

    DING_TALK_URL = os.environ.get("DING_TALK_URL", "https://oapi.dingtalk.com/robot/send?access_token=#")

    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", True)


class Config(BaseConfig):

    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "bigquant")
    DB_HOST = os.environ.get("DB_HOST", None)
    DB_PORT = os.environ.get("DB_PORT", None)
    DB_USER = os.environ.get("DB_USER", None)
    DB_PASSWORD = os.environ.get("DB_PASSWORD", None)
    DB_NAME = os.environ.get("DB_NAME", None)

    REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
    SQLALCHEMY_DATABASE_URI = 'postgresql+pygresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", False)


class TestConfig(BaseConfig):

    SECRET_KEY = '~!I am a informer the quick brown fox jumps over the lazy dog.-=:'
    DEBUG = True
    # debug show sql
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:123456@127.0.0.1:5432/bigvmatch'


class UnitTestConfig(BaseConfig):

    TESTING = True
    SECRET_KEY = 'Its test'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


def get_config(env):

    if env == 'test':
        return TestConfig
    elif env == 'unittest':
        return UnitTestConfig
    return Config
