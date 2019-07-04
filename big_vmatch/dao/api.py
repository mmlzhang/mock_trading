
from datetime import datetime, timedelta
from itertools import groupby

from flask import g

from . import db
from .models.vmatch import Fund, UserStock, Order
from ..exceptions import ObjectException, MessageContentException
from ..constant import DAY_FORMAT, DATE_FORMAT
from ..utils.dto_vmatch import OrderStatus, OrderCategory


def get_user_fund(user_id):
    return db.session.query(Fund).filter(Fund.user_id == user_id).first()


def get_fund_amount_freeze(user_id):
    fund = db.session.query(Fund).filter(Fund.user_id == user_id).first()
    if not fund or not fund.amount:
        raise ObjectException("you don't have fund, please recharge it")
    freeze = fund.freeze if fund.freeze else 0
    return fund.amount, freeze


def freeze_user_fund(order):
    fund = get_user_fund(g.user.id)
    if not fund.freeze:
        fund.freeze = 0
    fund.freeze = fund.freeze + int(order.count) * float(order.price)
    if fund.freeze > fund.amount:
        raise MessageContentException("you fund don't enough!")
    db.session.add(fund)
    db.session.commit()


def get_available_user_fund(user_id):
    amount, freeze = get_fund_amount_freeze(user_id)
    return amount - freeze


def get_order_list(user_id, instrument_id=None, status=None):
    db_query = db.session.query(Order).filter(Order.user_id == user_id)
    if instrument_id:
        db_query = db_query.filter(Order.instrument_id == instrument_id)
    if status:
        db_query = db_query.filter(Order.status == status)
    return db_query.all()


def add_user_stock_by_order(order):
    # 增加用户持仓
    user_stock = UserStock()
    user_stock.user_id = order.user_id
    user_stock.instrument_id = order.instrument_id
    user_stock.count = order.count
    user_stock.price = order.price
    user_stock.create_time = datetime.now()
    db.session.add(user_stock)
    db.session.commit()


def get_user_stocks(user_id, instrument_id=None, freeze=False, limit_date=None):
    """
    获取用户持仓数据
    Args:
        user_id: str
        instrument_id: str
        freeze: bool
        limit_date: date  日期在此日期之前的股票

    Returns: dict
                {instrument_id: [ list of user_stock object], ...}

    """
    db_query = db.session.query(UserStock).\
        filter(UserStock.user_id == user_id).\
        filter(UserStock.freeze.is_(freeze))
    if instrument_id:
        db_query = db_query.filter(UserStock.instrument_id == instrument_id)
    if limit_date:
        db_query = db_query.filter(UserStock.create_time <= limit_date)
    return {instrument_id: [s for s in stocks] for instrument_id, stocks in
            groupby(db_query.all(), key=lambda x: x.instrument_id)}


def get_available_user_stocks(user_id, instrument_id):
    limit_date = datetime.now() - timedelta(days=1)
    limit_date = datetime.strptime("{} 23:59:59".format(datetime.strftime(limit_date, DAY_FORMAT)), DATE_FORMAT)
    user_stock_dict = get_user_stocks(user_id=user_id, instrument_id=instrument_id,
                                      freeze=False, limit_date=limit_date)
    return user_stock_dict


def get_available_user_stocks_count(user_id, instrument_id) -> int:
    # 用户可交易持仓数为  总持仓数 - 冻结持仓数 - 不是T+1限制的持仓(不是当天买入的持仓)
    user_stock_dict = get_available_user_stocks(user_id=user_id, instrument_id=instrument_id)
    stocks = user_stock_dict.get(instrument_id)
    available_count = 0 if not stocks else sum([s.count for s in stocks])
    freeze_count = 0
    if stocks:
        freeze_stocks = get_user_stocks(user_id, instrument_id, freeze=True).get(instrument_id)
        freeze_count = 0 if not freeze_stocks else sum([s.count for s in freeze_stocks])
    return available_count - freeze_count


def _decrease_user_stock(us_list, count):
    for us in us_list:
        if count:
            if us.count <= count:
                db.session.delete(us)
                db.session.commit()
                count -= us.count
            else:
                us.count -= count
                db.session.add(us)
                db.session.commit()
                count = 0


def decrease_user_stock(user_id, instrument_id, count):
    # 减少用户持仓, 减少用户的freeze和总的持仓
    available_user_stocks = get_available_user_stocks(user_id, instrument_id).get(instrument_id)
    freeze_user_stocks = get_user_stocks(user_id, instrument_id=instrument_id, freeze=True).get(instrument_id)
    _decrease_user_stock(available_user_stocks, int(count))
    _decrease_user_stock(freeze_user_stocks, int(count))


def release_freeze_user_stock(freeze_user_stocks, count):
    _decrease_user_stock(freeze_user_stocks, int(count))


def freeze_user_stock(instrument_id, count, price, user_id):
    user_stock = UserStock()
    user_stock.instrument_id = instrument_id
    user_stock.count = count
    user_stock.price = price
    user_stock.user_id = user_id
    user_stock.freeze = True
    user_stock.create_time = datetime.now()
    db.session.add(user_stock)
    db.session.commit()


def process_orders(order_list, now_price_map):
    """
    检查当前待交易委托状态,是否达到交易条件

    Args:
        order_list: list[order object]  当前待交易委托列表
        now_price_map: dict  {instrument_id: now_price}

    Returns: list[order object unfinished]

    """
    unfinish_orders = []
    for order in order_list:
        now_price = now_price_map.get(order.instrument_id)
        if order.category == OrderCategory.buy and float(order.price) >= float(now_price):
            order.status = OrderStatus.finish
            # 扣款 增加用户持仓
            add_user_stock_by_order(order)

            fund = db.session.query(Fund).filter(Fund.user_id == g.user.id).first()
            fund.freeze -= float(order.price) * int(order.count)
            fund.amount -= float(order.price) * int(order.count)
            db.session.add(fund)

            db.session.add(order)
        elif order.category == OrderCategory.sell and float(order.price) <= float(now_price):
            order.status = OrderStatus.finish
            # 减少用户持仓
            decrease_user_stock(user_id=order.user_id, instrument_id=order.instrument_id, count=int(order.count))

            # 增加成交款
            fund = db.session.query(Fund).filter(Fund.user_id == g.user.id).first()
            fund.amount += float(order.price) * int(order.count)
            db.session.add(fund)

            db.session.add(order)
        else:
            unfinish_orders.append(order)
    db.session.commit()
    return unfinish_orders
