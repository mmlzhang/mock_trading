
from flask import Blueprint, jsonify, request

from .quotations import quotation_keys
from .quotations.api import get_free_quotations
from .utils.dto_vmatch import get_name_cn
from .exceptions import MessageContentException
from .quotations.api import is_instrument_id

quotation_blueprint = Blueprint('quotation', __name__)


@quotation_blueprint.route("/api/quotation", methods=["GET"])
def get_instrument_quotation():
    instrument_id = request.args.get("instrumentId", "000001").strip()
    if not is_instrument_id(instrument_id):
        raise MessageContentException("股票代码错误!")
    quotation = get_free_quotations(instrument_id).get(instrument_id)
    if quotation:
        result = []
        for k in quotation_keys[1:]:
            result.append({"key": get_name_cn(k), "value": quotation.get(k, "")})
        return jsonify(result)
    return jsonify([])
