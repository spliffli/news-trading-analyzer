import duka.app.app as import_ticks
from duka.core.utils import TimeFrame
import datetime

start_date = datetime.date(2023, 2, 3)
end_date = datetime.date(2023, 2, 3)
assets = ["EURUSD"]

import_ticks(assets, start_date, end_date, 4, TimeFrame.TICK, ".", True)