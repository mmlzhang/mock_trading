
import os


# 项目文件目录，基础目录    配置静态文件目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(TEMPLATES_DIR, 'static')
BQ_INSTRUMENTS = os.path.join(BASE_DIR, '../data/bigquant_instruments.txt')

# 环境
ENVIRONMENT = os.environ.get("ENVIRONMENT", "test")

# 时间字符串格式化
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DAY_FORMAT = "%Y-%m-%d"

# 前端http请求token
HEADER_TOKEN_NAME = "Authorization"
TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 7  # token过期时间,7天,后期缩短
TOKEN_CREATE_TIME = "create_time"

# 用户密码salt
PASSWORD_SALT1 = "bigquant1"
PASSWORD_SALT2 = "bigquant2"

# 用户注册口令
# REGISTER_TOKEN = "bigquant"


# 股票行情设置
DEFAULT_INSTRUMENT_ID = "000001"

INSTRUMENT_FILE_PATH = os.path.join(os.path.dirname(BASE_DIR), "data/bigquant_instruments.txt")
