# coding:utf8
import random
import re
from datetime import datetime

from . import basequotation


class Sina(basequotation.BaseQuotation):
    """新浪免费行情获取"""

    max_num = 800
    grep_detail = re.compile(
        r"(\d+)=[^\s]([^\s,]+?)%s%s"
        % (r",([\.\d]+)" * 29, r",([-\.\d:]+)" * 2)
    )
    grep_detail_with_prefix = re.compile(
        r"(\w{2}\d+)=[^\s]([^\s,]+?)%s%s"
        % (r",([\.\d]+)" * 29, r",([-\.\d:]+)" * 2)
    )

    @property
    def stock_api(self) -> str:
        return "http://hq.sinajs.cn/rn={}&list=".format(self._random())

    @staticmethod
    def _random(length=13) -> str:
        start = 10 ** (length - 1)
        end = (10 ** length) - 1
        return str(random.randint(start, end))

    def format_response_data(self, rep_data, prefix=False):
        stocks_detail = "".join(rep_data)
        grep_str = self.grep_detail_with_prefix if prefix else self.grep_detail
        result = grep_str.finditer(stocks_detail)
        stock_dict = dict()
        for stock_match_object in result:
            stock = stock_match_object.groups()
            stock_dict[stock[0]] = dict(
                name=stock[1],
                open=float(stock[2]),
                close=float(stock[3]),
                now=float(stock[4]),
                high=float(stock[5]),
                low=float(stock[6]),
                # buy=float(stock[7]),
                # sell=float(stock[8]),
                volume=int(stock[9]),
                turnover=float(stock[10]),
                bid1_volume=int(stock[11]),
                bid1=float(stock[12]),
                bid2_volume=int(stock[13]),
                bid2=float(stock[14]),
                bid3_volume=int(stock[15]),
                bid3=float(stock[16]),
                bid4_volume=int(stock[17]),
                bid4=float(stock[18]),
                bid5_volume=int(stock[19]),
                bid5=float(stock[20]),
                ask1_volume=int(stock[21]),
                ask1=float(stock[22]),
                ask2_volume=int(stock[23]),
                ask2=float(stock[24]),
                ask3_volume=int(stock[25]),
                ask3=float(stock[26]),
                ask4_volume=int(stock[27]),
                ask4=float(stock[28]),
                ask5_volume=int(stock[29]),
                ask5=float(stock[30]),
                datetime=datetime.strptime("{} {}".format(stock[31], stock[32]), "%Y-%m-%d %H:%M:%S")
            )
        return stock_dict
