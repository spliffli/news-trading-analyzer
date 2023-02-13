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


def haawks_id_to_str(haawks_id: float):
    # All haawks IDd should be 5 digits long but when they're stored as float or int inside the csv or excel files, it removes the leading zeros, so this adds them back
    return str(haawks_id).zfill(5)

