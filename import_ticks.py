import duka.app.app as duka_import
from duka.core.utils import TimeFrame
import datetime

start_date = datetime.date(2023, 2, 3)
end_date = datetime.date(2023, 2, 3)
assets = ["EURUSD"]

# duka_import(assets, start_date, end_date, 4, TimeFrame.TICK, ".", True)


def import_ticks(asset: str, date: datetime.date): # Wrapper function with fewer params. It imports ticks for one day
    duka_import([asset], date, date, 1, TimeFrame.TICK, "tick_data/", True)
