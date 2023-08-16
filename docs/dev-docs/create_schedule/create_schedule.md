# *create_schedule*

On this page I'll write pseudocode of the execution of this function which is an 'entry point' for this program. I'll do the same for the ranker later.

## Pseudocode

```
FUNCTION create_schedule(next_week, custom_date, update_news_and_tick_data):
    1. READ Excel file "reports/top_indicators.xlsx" INTO variable "top_indicators"
    2. INITIALIZE empty list "indicators"

    3. FOR each "index" and "row" in "top_indicators":
        3.1 APPEND tuple (inv_id, haawks_id_str, symbol, higher_dev, inv_title) TO "indicators"
    4. END FOR

    5. CALL function scrape_economic_calendar with "indicators", "next_week" and "custom_date"
       and STORE result INTO "upcoming_events"
    6. STORE length of "upcoming_events" INTO "no_of_events"

    7. INITIALIZE "weekdays_html" with keys as days of the week and values as empty strings

    8. IF "update_news_and_tick_data" is True:
        8.1 PRINT message about updating news and tick data for upcoming events
        8.2 FOR each "index" and "event" in "upcoming_events":
            8.2.1 EXTRACT relevant fields from "event"
            8.2.2 PRINT progress message
            8.2.3 CALL function update_indicator_history with "haawks_id_str"
            8.2.4 PRINT message about importing ticks
            8.2.5 CALL function import_ticks_for_indicator with "haawks_id_str" and "symbol"
        8.3 END FOR
    9. END IF

    10. PRINT message about analyzing and generating recommended triggers for events

    11. FOR each "index" and "event" in "upcoming_events":
        11.1 EXTRACT relevant fields from "event"
        11.2 PRINT progress message
        11.3 CALCULATE "dt_gmt" and formatted date strings "datetime_et_str" and "datetime_str"
        11.4 CALL function get_triggers_vars with "haawks_id_str", "symbol", "higher_dev" 
             and STORE result INTO "triggers_vars"
        11.5 CALL function get_day with "dt_gmt" and STORE result INTO "day"
        11.6 IF "triggers_vars" is "Not enough data" OR "lowest_c_3_val too low":
            11.6.1 SET "event_html" to an empty string
        11.7 ELSE:
            11.7.1 CALL function render_event_html with arguments "title", "datetime_str", 
                    "datetime_et_str", "symbol", "triggers_vars" and STORE result INTO "event_html"
        11.8 END IF
        11.9 APPEND "event_html" to the appropriate day in "weekdays_html"
    12. END FOR

    13. INITIALIZE "template_vars" dictionary with various date and events details

    14. CALL function generate_weekly_schedule with "template_vars"
    
END FUNCTION
```

## Pseudocode and Descriptions for `create_schedule` Function

### **Step 1**

```
1. READ Excel file "reports/top_indicators.xlsx" INTO variable "top_indicators"
```

**What:** This line is reading an Excel file named "top_indicators.xlsx" and storing its contents in a variable called "top_indicators".

**Why:** The Excel file likely contains information on key economic indicators that the program will later use for analysis. This is the starting point, as we need to know which indicators we are going to analyze.


### **Step 2**

```
2. INITIALIZE empty list "indicators"
```

**What:** This line is initializing an empty list named "indicators".

**Why:** This list will be used to store tuples containing information about each economic indicator. We need this list to keep track of the indicators that we are going to analyze based on the input data.


### **Step 3**

```
3. FOR each "index" and "row" in "top_indicators":
   3.1 APPEND tuple (inv_id, haawks_id_str, symbol, higher_dev, inv_title) TO "indicators"
4. END FOR
```

**What:** This loop iterates through each row in the "top_indicators" DataFrame (read from the Excel file), and for each row, it creates a tuple containing specific information about an economic indicator. This tuple is then appended to the "indicators" list.

**Why:** This is done to transform the raw data from the Excel file into a structured list of indicators, with relevant information neatly packed into tuples. We need this structured data for later stages of analysis.


### **Step 5**

```
5. CALL function scrape_economic_calendar with "indicators", "next_week" and "custom_date"
   and STORE result INTO "upcoming_events"
```

**What:** This line is calling a function named scrape_economic_calendar, passing in the "indicators" list, and two other parameters "next_week" and "custom_date". The result of this function call is stored in a variable named "upcoming_events".

**Why:** This is done to fetch a schedule of upcoming economic events (news releases, reports, etc.) from investing.com based on the given indicators. We need this schedule to know when each indicator will have new data released, which the program will later analyze.


### **Step 6**

```
6. STORE length of "upcoming_events" INTO "no_of_events"
```

**What:** This line is calculating the length (number of elements) of the "upcoming_events" list and storing it in a variable called "no_of_events".

**Why:** This is done to keep track of the total number of upcoming economic events that the program will analyze. This count is likely used for progress tracking, as we loop through and process each of these events.


### **Step 7**

```
7. INITIALIZE "weekdays_html" with keys as days of the week and values as empty strings
```

**What:** This line is initializing a dictionary named "weekdays_html", where the keys are the names of the days of the week and the values are empty strings.

**Why:** This dictionary is used to store HTML content related to each day of the week. This seems to prepare for generating a weekly schedule or report, where each day may have different economic events associated with it.