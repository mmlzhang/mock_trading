
from .free_stock import sina, tencent
from ..exceptions import MessageContentException
from ..constant import INSTRUMENT_FILE_PATH


def get_bigquant_instrument(market=False) -> list:
    """
    get instrument from bigquant.com

    Args:
        market: bool  是否给出market 交易所缩写

    Returns:
        market = True
            ['000001.SZA', '000002.SZA', '600992.SHA', '600993.SHA' ....]
        market = False
            ['000001', '000002', '600992', '600993' ....]
    """
    with open(INSTRUMENT_FILE_PATH, 'r', encoding="utf-8") as file:
        instruments = file.read().split(",")
        return instruments if market else [i.split(".")[0] for i in instruments]


def is_instrument_id(instrument_id) -> bool:
    """

    Args:
        instrument_id: str

    Returns: bool   True / False

    """
    if instrument_id in get_bigquant_instrument(market=False):
        return True
    return False


def get_free_quotations(instruments):
    """
    get free quotation from free api sina and tencent

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
    get now price from free quotation api

    Args:
        instrument_ids: list[str]

    Returns: dict
                {instrument_id: now_price, ...}

    """
    quotations = get_free_quotations(list(set(instrument_ids)))
    if not quotations:
        raise MessageContentException("股票代码错误, 重新输入!")
    return {instrument_id: quotations.get(instrument_id).get("now") for instrument_id in instrument_ids}
