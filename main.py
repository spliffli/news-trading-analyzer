import time
import os

from import_ticks import import_ticks_for_indicator
from analyze_data import read_news_data, read_triggers, load_news_pip_data, calc_news_pip_metrics, news_pip_metrics_to_dfs
from scrape import update_indicator_history

try:
    import curses  # Try to import the curses module
except ImportError:

    if os.name == 'nt':
        import windows_curses as curses  # If curses isn't available, try to import the Windows-specific version
    else:
        raise  # If neither curses nor windows_curses are available, raise an ImportError


class MyApp:
    def __init__(self):
        # Initialize a curses screen
        self.stdscr = curses.initscr()

        # Configure the screen
        curses.curs_set(0)  # Make the cursor invisible
        curses.noecho()  # Don't show typed characters on the screen
        curses.cbreak()  # React to key presses immediately
        self.stdscr.keypad(True)  # Enable special keys like the function keys and arrow keys

        # Define a list of items to display and analyze
        self.header = "Please select an indicator to analyze:"
        self.items = [
            "30000  U.S. Crude Oil Inventories",
            "30001  U.S. Gasoline Inventories",
            "30002  U.S. Distillate Fuel Production",
            "30008  U.S. Cushing Crude Oil Inventories",
            "30010  U.S. Natural Gas Storage",
            "10000  U.S. Nonfarm Payrolls",
            "10005  U.S. Unemployment Rate",
            "10010  U.S. Producer Price Index (PPI) MoM",
            "10011  U.S. Producer Price Index (PPI) YoY",
            "10012  U.S. Core Producer Price Index (PPI) MoM",
            "10013  U.S. Core Producer Price Index (PPI) YoY",
            "10020  U.S. Import Price Index MoM",
            "10022  U.S. Export Price Index MoM",
            "10030  U.S. Consumer Price Index (CPI) MoM",
            "10031  U.S. Consumer Price Index (CPI) YoY",
            "10032  U.S. Core Consumer Price Index (CPI) MoM",
            "10033  U.S. Core Consumer Price Index (CPI) YoY",
            "10034  U.S. Consumer Price Index (CPI) Index, n.s.a.",
            "10037  U.S. Core Consumer Price Index (CPI) Index",
            "10040  U.S. Industrial Production MoM",
            "10041  U.S. Industrial Production YoY",
            "10042  U.S. Capacity Utilization Rate",
            "10044  U.S. Manufacturing Production MoM",
            "10060  U.S. Gross Domestic Product (GDP) QoQ",
            "10061  U.S. Gross Domestic Product (GDP) Price Index QoQ",
            "10070  U.S. Personal Spending MoM",
            "10071  U.S. Core PCE Price Index MoM",
            "10072  U.S. Core PCE Price Index YoY",
            "10073  U.S. PCE price index",
            "10074  U.S. PCE Price index YoY",
            "10075  U.S. Personal Income MoM",
            "10076  U.S. Real Personal Consumption MoM",
            "10080  U.S. JOLTs Job Openings",
            "10090  U.S. Michigan Consumer Sentiment",
            "10091  U.S. Michigan Inflation Expectations",
            "10092  U.S. Michigan Current Conditions",
            "10100  U.S. Trade Balance",
            "10110  U.S. Factory Orders MoM",
            "10120  U.S. Wholesale Inventories MoM",
            "10130  U.S. Retail Sales MoM",
            "10132  U.S. Core Retail Sales MoM",
            "10140  U.S. Business Inventories MoM",
            "10150  U.S. Housing Starts MoM",
            "10152  U.S. Housing Starts",
            "10154  U.S. Building Permits MoM",
            "10156  U.S. Building Permits",
            "10160  U.S. New Home Sales MoM",
            "10162  U.S. New Home Sales",
            "10170  U.S. Durable Goods Orders MoM",
            "10172  U.S. Core Durable Goods Orders MoM",
            "10180  U.S. Retail Inventories Excluding Auto",
            "10190  U.S. Goods Trade Balance",
            "10200  U.S. Wholesale Inventories MoM",
            "10210  U.S. Construction Spending MoM",
            "10220  U.S. Employment Cost Index QoQ",
            "10230  U.S. Initial Jobless Claims",
            "10240  Fed Interest Rate Decision",
            "10242  U.S. Federal Open Market Committee (FOMC) Statement",
            "10250  Canada Consumer Price Index (CPI) MoM",
            "10251  Canada Consumer Price Index (CPI) YoY",
            "10252  Canada Core Consumer Price Index (CPI) MoM",
            "10253  Canada Core Consumer Price Index (CPI) YoY",
            "10260  Canada Core Retail Sales MoM",
            "10261  Canada Retail Sales MoM",
            "10270  Canada Gross Domestic Product (GDP) MoM",
            "10272  Canada Gross Domestic Product (GDP) YoY",
            "10280  Canada Trade Balance",
            "10281  Canada Exports",
            "10282  Canada Imports",
            "10290  Canada Employment Change",
            "10291  Canada Unemployment Rate",
            "10292  Canada Full Employment Change",
            "10293  Canada Part Time Employment Change",
            "10294  Canada Participation Rate",
            "10300  Canada Building Permits MoM",
            "10310  Canada New Housing Price Index MoM",
            "10320  Canada Manufacturing Sales MoM",
            "10330  Canada Foreign Securities Purchases",
            "10331  Foreign Securities Purchases by Canadians",
            "10340  Canada Wholesale Sales MoM",
            "10350  Canada Current Account",
            "10360  Canada Industrial Product Price Index (IPPI) MoM",
            "10361  Canada Industrial Product Price Index (IPPI) YoY",
            "10370  Canada Raw Materials Price Index (RMPI) MoM",
            "10371  Canada Raw Materials Price Index (RMPI) YoY",
            "10380  Canada Labor Productivity QoQ",
            "10390  Canada Gross Domestic Product (GDP) Annualized QoQ",
            "00003  Russia Interest Rate Decision",
            "00013  Turkey One-Week Repo Rate",
            "00017  Norway Interest Rate Decision",
            "00021  Eurozone Interest Rate Decision",
            "00041  Norway Consumer Price Index (CPI) MoM",
            "00042  Norway Consumer Price Index (CPI) YoY",
            "00047  Norway Core Retail Sales MoM",
            "00049  Norway Unemployment Rate",
            "00091  Norway Gross Domestic Product (GDP) QoQ",
            "00092  Norway Gross Domestic Product (GDP) Mainland QoQ",
            "00051  Sweden Consumer Price Index (CPI) MoM",
            "00052  Sweden Consumer Price Index (CPI) YoY",
            "00053  Sweden Consumer Price Index at Constant Interest Rates (CPIF) MoM",
            "00054  Sweden Consumer Price Index at Constant Interest Rates (CPIF) YoY",
            "00057  Sweden Retail Sales MoM",
            "00058  Sweden Retail Sales YoY",
            "00059  Sweden Unemployment Rate",
            "00071  Sweden Gross Domestic Product (GDP) QoQ",
            "00072  Sweden Gross Domestic Product (GDP) YoY",
            "00141  Poland Interest Rate Decision"
        ]

        # Keep track of the currently selected item and the first visible item
        self.selected_item_index = 0
        self.start_index = 0

    def get_max_display_items(self):
        # Calculate the maximum number of items that can fit on the screen
        return curses.LINES - 3  # Account for header and prompt

    def run(self):
        self.max_display_items = self.get_max_display_items()

        # Display the initial list of items
        self.render()

        while True:
            # Wait for a key press
            key = self.stdscr.getch()

            # Handle up arrow key
            if key == curses.KEY_UP and self.selected_item_index > 0:
                self.selected_item_index -= 1
                if self.selected_item_index < self.start_index:
                    self.start_index -= 1
                self.render()

            # Handle down arrow key
            elif key == curses.KEY_DOWN and self.selected_item_index < len(self.items) - 1:
                self.selected_item_index += 1
                if self.selected_item_index >= self.start_index + self.max_display_items:
                    self.start_index += 1
                self.render()

            # Handle enter key
            elif key == curses.KEY_ENTER or key in [10, 13]:
                selected_item = self.items[self.selected_item_index]
                haawks_id_str = selected_item.split()[0]
                self.analyze_indicator(haawks_id_str)

    def render(self):
        # Clear the screen
        self.stdscr.clear()

        # Print header
        self.stdscr.addstr(0, 0, self.header, curses.A_REVERSE)

        # Print list items
        for i, item in enumerate(self.items[self.start_index:self.start_index + self.max_display_items]):
            display_index = self.start_index + i
            if display_index == self.selected_item_index:
                # Highlight the currently selected item
                self.stdscr.addstr(i + 2, 0, item, curses.A_STANDOUT)
            else:
                self.stdscr.addstr(i + 2, 0, item)

        self.stdscr.refresh()

    def analyze_indicator(self, haawks_id_str):
        # Clear the screen and display a message indicating which indicator is being analyzed
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Analyzing indicator {haawks_id_str}...")
        self.stdscr.refresh()

        # End the curses environment to allow normal printing
        curses.endwin()

        # Determine the name of the operating system we're running on,
        # and then execute the appropriate command to clear the screen.
        os.system('cls' if os.name == 'nt' else 'clear')

        # Prompt the user to enter a trading symbol
        print("Please enter a trading symbol e.g. 'EURUSD': ")

        # Get the user's input as a string (up to 20 characters long)
        trading_symbol = input()[:20]

        # Perform analysis on the selected indicator and trading symbol
        news_data = update_indicator_history(haawks_id_str)
        import_ticks_for_indicator(haawks_id_str, trading_symbol)
        triggers = read_triggers(haawks_id_str)
        news_pip_data = load_news_pip_data(haawks_id_str, news_data, trading_symbol)
        news_pip_metrics = calc_news_pip_metrics(news_pip_data, triggers, higher_dev="bearish")
        news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)

        # Reinitialize the curses environment
        # self.stdscr = curses.initscr()
        # self.render()


    def __del__(self):
        # End curses window when program terminates
        if hasattr(self, 'stdscr'):
            curses.endwin()


if __name__ == "__main__":
    # Create and run the application
    app = MyApp()
    app.run()
