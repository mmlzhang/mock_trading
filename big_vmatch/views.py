
from datetime import datetime

from flask import Blueprint, render_template, jsonify, request, g

from big_vmatch import __version__
from .dao import db
from .dao.api import get_available_user_fund, get_available_user_stocks_count, get_order_list, process_orders, \
    freeze_user_fund, freeze_user_stock, get_user_stocks, release_freeze_user_stock
from .dao.models.vmatch import Order, Fund, UserStock
from .utils.dto_vmatch import OrderStatus, OrderCategory
from .author import login_required
from .constant import DEFAULT_INSTRUMENT_ID
from .status_code import SUCCESS_CODE
from .exceptions import MessageContentException
from .quotations.api import get_now_price_map, is_instrument_id

main_blueprint = Blueprint('trading', __name__)


@main_blueprint.route('/')
def index():
    return render_template('index.html')


@main_blueprint.route("/api/version")
def version():
    return jsonify({"version": __version__})


@main_blueprint.route("/api/orders/current", methods=["GET"])
@login_required
def get_current_order():
    # 当前委托列表
    order_list = get_order_list(g.user.id, status=OrderStatus.pending)
    # 对比实时行情,如果达到成交条件,使委托成交  买入-增加持仓 卖出-减少持仓
    if order_list:
        now_price_map = get_now_price_map(instrument_ids=[o.instrument_id for o in order_list])
        order_list = process_orders(order_list, now_price_map=now_price_map)
    return jsonify([order.to_dict() for order in order_list])


@main_blueprint.route("/api/orders", methods=["GET"])
@login_required
def get_orders():
    order_list = get_order_list(g.user.id)
    return jsonify([order.to_dict() for order in order_list])


@main_blueprint.route("/api/order/<option>", methods=["POST"])
@login_required
def option_order(option):
    # 买入/卖出 委托
    instrument_id = request.json.get("id") if request.json.get("id") else DEFAULT_INSTRUMENT_ID
    if not is_instrument_id(instrument_id):
        raise MessageContentException("股票代码错误!")
    count = request.json.get("count")
    price = request.json.get("price")
    order = Order()
    order.status = OrderStatus.pending
    order.user_id = g.user.id
    order.instrument_id = instrument_id
    order.count = count
    order.price = price
    order.create_time = datetime.now()
    order.update_time = datetime.now()
    if option == OrderCategory.buy:
        order.category = OrderCategory.buy
        order_price = float(order.price) * int(order.count)
        if order_price > get_available_user_fund(g.user.id):
            raise MessageContentException("Your order beyond your fund!")
        # 冻结资金
        freeze_user_fund(order)
    elif option == OrderCategory.sell:
        # 将持仓股票卖出, 减少用户持仓, T+1
        order.category = OrderCategory.sell
        available_user_stocks = get_available_user_stocks_count(user_id=order.user_id,
                                                                instrument_id=order.instrument_id)
        if int(order.count) > available_user_stocks:
            raise MessageContentException("You don't have enough stocks!")
        # 冻结股票
        freeze_user_stock(instrument_id=order.instrument_id, count=order.count,
                          price=order.price, user_id=order.user_id)

    now_price_map = get_now_price_map(instrument_ids=[order.instrument_id])
    process_orders([order], now_price_map=now_price_map)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict())


@main_blueprint.route("/api/order/cancel", methods=["PUT"])
@login_required
def cancel_order():
    # 取消委托,讲冻结的资金和股票归还
    order_id = request.json.get("id")
    order = db.session.query(Order).filter(Order.id == order_id).first()
    order.status = OrderStatus.cancel
    if order.category == OrderCategory.buy:
        # 释放被冻结的资金
        user_fund = db.session.query(Fund).filter(Fund.user_id == order.user_id).first()
        user_fund.freeze -= order.price * order.count
        db.session.add(user_fund)
    if order.category == OrderCategory.sell:
        # 释放被冻结的股票
        user_freeze_stocks = get_user_stocks(user_id=order.user_id,
                                             instrument_id=order.instrument_id, freeze=True).get(order.instrument_id)
        release_freeze_user_stock(user_freeze_stocks, order.count)
    order.update_time = datetime.now()
    db.session.add(order)
    db.session.commit()
    return jsonify(SUCCESS_CODE)


@main_blueprint.route("/api/stock/user", methods=["GET"])
@login_required
def get_user_stock_api():
    user_stocks = get_user_stocks(user_id=g.user.id)
    result = []
    num = 0
    for instrument_id, stocks in user_stocks.items():
        num += 1
        count = sum([s.count for s in stocks])
        total = sum([s.count * s.price for s in stocks])
        available_user_stocks_count = get_available_user_stocks_count(user_id=g.user.id, instrument_id=instrument_id)
        data_dict = {
            "instrument_id": instrument_id,
            "count": count,
            "available_count": available_user_stocks_count,
            "price": total,
            "unit_price": total / count,
            "id": num
        }
        result.append(data_dict)
    return jsonify(result)


@main_blueprint.route("/api/edit/quotation", methods=["PUT"])
@login_required
def edit_quotation():
    # 修改股票当前的价格, 检查已有委托是否达可以成交
    instrument_id = request.json.get("id") if request.json.get("id") else DEFAULT_INSTRUMENT_ID
    if not is_instrument_id(instrument_id):
        raise MessageContentException("股票代码错误!")
    price = float(request.json.get("price").strip())
    order_list = get_order_list(user_id=g.user.id, instrument_id=instrument_id, status=OrderStatus.pending)
    now_price_map = {instrument_id: price}
    if order_list:
        process_orders(order_list, now_price_map=now_price_map)
    return jsonify(SUCCESS_CODE)


@main_blueprint.route("/api/rebuild/tables")
def create_tables():
    db.drop_all()
    db.create_all()
    return jsonify(SUCCESS_CODE)


@main_blueprint.route("/api/clean/data")
@login_required
def clean_data():
    orders = db.session.query(Order).filter(Order.user_id == g.user.id).all()
    fund = db.session.query(Fund).filter(Fund.user_id == g.user.id).all()
    user_stocks = db.session.query(UserStock).filter(UserStock.user_id == g.user.id).all()
    for t in orders + fund + user_stocks:
        db.session.delete(t)
        db.session.commit()
    return jsonify(SUCCESS_CODE)
