from datetime import datetime


def datetime_to_str(dt: datetime, microseconds=False):
    if not microseconds:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif microseconds:
        return dt.strftime("%Y-%m-%d %H:%M:%S:%f")


def str_to_datetime(dt_str: str):
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S:%f")
