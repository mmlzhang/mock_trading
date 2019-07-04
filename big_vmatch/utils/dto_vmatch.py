
from ..exceptions import MessageContentException


def _is_status(cls, status):
    if not status or not isinstance(status, str):
        raise MessageContentException("status is must and type must string")
    return True if status in [i for i in cls.__dict__.values() if
                              isinstance(i, str) and not i.startswith("_")] else False


class OrderStatus(object):

    pending = "pending"
    finish = "finish"
    reject = "reject"
    cancel = "cancel"

    @staticmethod
    def is_status(status):
        return _is_status(OrderStatus, status)


class OrderCategory(object):

    buy = "buy"
    sell = "sell"


class Category(object):

    stock = "stock"  # 股票
    futures = "futures"  # 期货


def get_name_cn(name_en):
    from ..quotations import sina_quotation_map

    name_map = {
        OrderCategory.buy: "买入",
        OrderCategory.sell: "卖出",
        Category.stock: "股票",
        Category.futures: "期货",
    }
    name_map.update(sina_quotation_map)
    return name_map.get(name_en)
