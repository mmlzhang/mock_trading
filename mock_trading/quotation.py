
from flask import Blueprint, jsonify, request

from .quotations import quotation_keys
from .quotations.api import get_current_quotations
from .utils.dto_vmatch import get_name_cn
from .quotations.api import get_now_price_map
from .exceptions import MessageContentException

quotation_blueprint = Blueprint('quotation', __name__)


@quotation_blueprint.route("/api/quotation", methods=["GET"])
def get_instrument_quotation():
    instrument_id = request.args.get("instrumentId", "000001").strip()
    if not get_now_price_map(instrument_ids=[instrument_id]).get(instrument_id):
        raise MessageContentException("股票代码错误!")
    quotation = get_current_quotations(instrument_id).get(instrument_id)
    if quotation:
        result = []
        for k in quotation_keys[1:]:
            result.append({"key": get_name_cn(k), "value": quotation.get(k, "")})
        return jsonify(result)
    return jsonify([])
