# -*- coding: utf-8 -*-


def parse_value_from_type(value):
    """
    类型转换
    :param value:
    :return:
    """
    if isinstance(value, int):
        return int(value)
    elif isinstance(value, float):
        return float(value)
    elif isinstance(value, list):
        # 判断是数组对象，返回数组
        return list(value)
    elif value.lower() == "false":
        return False
    elif value.lower() == "true":
        return True
    else:
        return str(value)
