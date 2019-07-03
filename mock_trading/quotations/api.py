
from .free_stock import sina, tencent
from ..exceptions import MessageContentException


def get_current_quotations(instruments):
    """

    Args:
        instruments: list

    Returns: {instrument_id: {quotations}, ...}

    """

    market = [sina, tencent]
    quotations = market[0].real(instruments)
    lost_instruments = [code for code in instruments if code not in quotations]
    lost_quotations = market[1].real(lost_instruments)
    quotations.update(lost_quotations)
    return quotations


def get_now_price_map(instrument_ids):
    """

    Args:
        instrument_ids: list[str]

    Returns: dict
                {instrument_id: now_price, ...}

    """
    quotations = get_current_quotations(list(set(instrument_ids)))
    if not quotations:
        raise MessageContentException("股票代码错误, 重新输入!")
    return {instrument_id: quotations.get(instrument_id).get("now") for instrument_id in instrument_ids}
