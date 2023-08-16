# scheduler.py

Execution call hierarchy/profile (manually written by stepping through code with debugger):

- `scheduler.create_schedule`
  - For each top indicator, get Haawks Id & append to indicators dict
    - `utils.haawks_id_to_str`
  - `scrape.scrape_economic_calendar`
    - `scrape.prepare_calendar`
  - `scrape.update_indicator_history`
    - `utils.get_indicator_info`
      - `utils.haawks_id_to_str`
    - `utils.datetime_to_str`
    - `scrape.expand_table`