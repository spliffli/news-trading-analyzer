import curses
import time

class MyApp:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        self.header = "Please select an indicator to analyze"
        self.items = [
            "30000 U.S. Crude Oil Inventories",
            "30001 U.S. Gasoline Inventories",
            "30002 U.S. Distillate Fuel Production",
            "30008 U.S. Cushing Crude Oil Inventories",
            "30010 U.S. Natural Gas Storage",
            "10000 U.S. Nonfarm Payrolls",
            "10005 U.S. Unemployment Rate",
            "10010 U.S. Producer Price Index (PPI) MoM",
            "10011 U.S. Producer Price Index (PPI) YoY",
            "10012 U.S. Core Producer Price Index (PPI) MoM",
            "10013 U.S. Core Producer Price Index (PPI) YoY",
            "10020 U.S. Import Price Index MoM",
            "10022 U.S. Export Price Index MoM",
            "10030 U.S. Consumer Price Index (CPI) MoM",
            "10031 U.S. Consumer Price Index (CPI) YoY",
            "10032 U.S. Core Consumer Price Index (CPI) MoM",
            "10033 U.S. Core Consumer Price Index (CPI) YoY",
            "10034 U.S. Consumer Price Index (CPI) Index, n.s.a.",
            "10037 U.S. Core Consumer Price Index (CPI) Index"
        ]
        self.selected_item_index = 0

    def run(self):
        self.render()

        while True:
            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.selected_item_index > 0:
                self.selected_item_index -= 1
                self.render()
            elif key == curses.KEY_DOWN and self.selected_item_index < len(self.items) - 1:
                self.selected_item_index += 1
                self.render()
            elif key == curses.KEY_ENTER or key in [10, 13]:
                selected_item = self.items[self.selected_item_index]
                indicator = selected_item.split()[0]
                self.analyze_indicator(indicator)

    def render(self):
        self.stdscr.clear()

        # Print header
        self.stdscr.addstr(0, 0, self.header, curses.A_REVERSE)

        # Print list items
        for i, item in enumerate(self.items):
            if i == self.selected_item_index:
                self.stdscr.addstr(i+2, 0, item, curses.A_STANDOUT)
            else:
                self.stdscr.addstr(i+2, 0, item)

        self.stdscr.refresh()

    def analyze_indicator(self, indicator):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Analyzing indicator {indicator}...")
        self.stdscr.refresh()

        self.stdscr.addstr(2, 0, "Please enter a trading symbol e.g. 'EURUSD': ")
        curses.echo()
        curses.cbreak()
        trading_symbol = self.stdscr.getstr(3, 0, 20).decode(encoding="utf-8")
        curses.noecho()
        curses.nocbreak()

        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Indicator: {indicator}")
        self.stdscr.addstr(1, 0, f"Trading Symbol: {trading_symbol}")
        self.stdscr.refresh()
        time.sleep(2)  # Sleep for 2 seconds to simulate analysis
        self.render()

    def __del__(self):
        curses.endwin()


if __name__ == "__main__":
    app = MyApp()
    app.run()
