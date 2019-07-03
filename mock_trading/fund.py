
from flask import Blueprint, jsonify, request, g

from .dao import db
from .dao.models.vmatch import Fund
from .author import login_required
from .status_code import SUCCESS_CODE
from .exceptions import MessageContentException

fund_blueprint = Blueprint('fund', __name__)


@fund_blueprint.route("/api/recharge", methods=["PUT"])
@login_required
def recharge():
    amount = request.json.get("amount").strip()
    if not amount:
        raise MessageContentException("amount cannot be None!")
    user = g.user
    fund = db.session.query(Fund).filter(Fund.user_id == user.id).first()
    if not fund:
        fund = Fund()
        fund.user_id = g.user.id
        fund.amount = int(amount)
    else:
        fund.amount += int(amount)
    # fund.update_time = datetime.now()
    db.session.add(fund)
    db.session.commit()

    return jsonify(SUCCESS_CODE)
