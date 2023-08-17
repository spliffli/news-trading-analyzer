# Excavation

!!! info
    In this document I'll be taking notes and documenting the process of getting back into this project. 
    As it has been 4 months since I last looked at it, it's just a faded memory and I while I must re-discover, define and improve upon the workflow that I had before.

## **Todo**

- [ ] Create markdown files for each `.py` file
- [ ] For each python file:
    - Go through each function and make sure each function has docstrings
    - Turn docstrings into documentation for the corresponding markdown file under its header.
    - Add additional notes about each function and try to identify where it.

---

## **Journal**

### **16.08.2023**

After looking at and stepping through some of my code, I figured out that the `create_schedule` function in the `scheduler` module is one of the entry points to this program. It assumes that the `top_indicators.xlsx` file is populated, and that is done by running the ranker and I manually did that. For now I'll focus on the scheduler and later I'll go back to the ranker which is the second entry point to this program.

Here is the pseudocode for `create_schedule`:

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


### **17.08.2023**

- [ ] blah
- [ ] blah
    - [x] blah