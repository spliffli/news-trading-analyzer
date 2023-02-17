import time

try:
    import curses  # Try to import the curses module
except ImportError:
    import os
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
            "30000 U.S. Crude Oil Inventories",
            "30001 U.S. Gasoline Inventories",
            "30002 U.S. Distillate Fuel Production",
            "30008 U.S. Cushing Crude Oil Inventories",
            "30010 U.S. Natural Gas Storage",
            "10000 U.S. Nonfarm Payrolls",
            "10005 U.S. Unemployment Rate",
            "10010 U.S. Producer Price Index (PPI) MoM",
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
                indicator = selected_item.split()[0]
                self.analyze_indicator(indicator)

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

    def analyze_indicator(self, indicator):
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Analyzing indicator {indicator}...")
        self.stdscr.refresh()

        # Prompt user to enter a trading symbol
        self.stdscr.addstr(2, 0, "Please enter a trading symbol e.g. 'EURUSD': ")
        curses.echo()
        curses.cbreak()
        trading_symbol = self.stdscr.getstr(3, 0, 20).decode(encoding="utf-8")
        curses.noecho()
        curses.nocbreak()

        # Display selected indicator and trading symbol
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Indicator: {indicator}")
        self.stdscr.addstr(1, 0, f"Trading Symbol: {trading_symbol}")

        # Perform analysis (simulated with a sleep)
        print("Hello World")
        self.stdscr.refresh()
        time.sleep(2)  # Sleep for 2 seconds to simulate analysis

        # Redraw menu
        self.render()

    def __del__(self):
        # End curses window when program terminates
        if hasattr(self, 'stdscr'):
            curses.endwin()

if __name__ == "__main__":
    # Create and run the application
    app = MyApp()
    app.run()
