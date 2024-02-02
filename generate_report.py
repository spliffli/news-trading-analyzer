import datetime
import markdown

from analyze_data import read_news_data, read_triggers, load_news_pip_data_at_timedeltas, calc_news_pip_metrics, \
    news_pip_metrics_to_dfs
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from utils import str_to_datetime
from pprint import pprint
import pandas as pd

env = Environment(loader=FileSystemLoader('.'))

"""
template_vars = {
    "title": "Canada Employment Change",
    "haawks_id_str": "10290",
    "symbol": "USDCAD",
    "importance": "***",
    "bullish_or_bearish": "bearish",
    "description": "",
    "no_of_releases": "73",
    "start_date": "2017-01-06",
    "end_date": "2023-01-06",
    "trigger_1_data": news_pip_metrics_dfs['trigger_1'].to_html(index=False),
    "trigger_2_data": news_pip_metrics_dfs['trigger_2'].to_html(index=False),
    "trigger_3_data": news_pip_metrics_dfs['trigger_3'].to_html(index=False),
    "trigger_4_data": news_pip_metrics_dfs['trigger_4'].to_html(index=False),
}


html_out = template.render(template_vars)
HTML(string=html_out).write_pdf("report-example.pdf", stylesheets=["reports/template/report-style.css"])
"""


def render_pdf_report(haawks_id_str, symbol, news_data, news_pip_metrics_dfs, triggers, symbol_higher_dev, indicator_info):
    template = env.get_template('reports/template/report-template.html')
    no_of_releases = news_data.shape[0]
    start_date = str_to_datetime(news_data.loc[no_of_releases -1]['Timestamp']).date()
    end_date = str_to_datetime(news_data.loc[0]['Timestamp']).date()

    match indicator_info['inv_importance']:
        case 1:
            importance = "*"
        case 2:
            importance = "**"
        case 3:
            importance = "***"

    template_vars = {
        "title": indicator_info['inv_title'],
        "haawks_id_str": haawks_id_str,
        "symbol": symbol,
        "importance": importance,
        "bullish_or_bearish": symbol_higher_dev,
        "description": indicator_info['inv_description'],
        "no_of_releases": no_of_releases,
        "start_date": start_date,
        "end_date": end_date,
        "suffix": indicator_info['suffix'],
    }

    for trigger in news_pip_metrics_dfs:
        template_vars[trigger] = triggers[trigger]
        template_vars[f"{trigger}_data"] = news_pip_metrics_dfs[trigger].to_html(index=False)

    print("Generating report...")
    html_out = template.render(template_vars)
    title_underscored = indicator_info['inv_title'].replace(" ", "_").replace(".", "").replace(",", "")
    filepath = f"reports/{haawks_id_str}_{symbol}_{title_underscored}__{start_date}_{end_date}.pdf"
    HTML(string=html_out).write_pdf(filepath, stylesheets=["reports/template/report-style.css"])
    print(f"Report saved to {filepath}")


def render_trigger_html(trigger):
    output_html = (f"            <h5>{trigger['lowest_c3_type']}: <span>{trigger['lowest_c3_val']}</span></h5>\n"
                   + f"            <h5>data pts: <span>{trigger['data_points']}</span></h5>\n"
                   + f"            <h5>dev: <span>{trigger['dev']}</span></h5>\n"
                   + f"            <h5>lots/€1k: <span>{trigger['lots_per_1000']}</span></h5>\n"
                   + f"            <h5>lots: <span>{trigger['lots']}</span></h5>\n")
    return output_html


def render_triggers_html(triggers_vars):
    output_html = ""
    for key in triggers_vars:
        match key:
            case 'lta':
                output_html += f"<h4>LTA: <span>{triggers_vars[key]}</span></h4>\n"
            case 'uta':
                output_html += (f"        <h4>UTA: <span>{triggers_vars[key]}</span></h4>\n"
                                + "        <br>\n")
            case "lower_triggers":
                output_html += '          <div class="lower-triggers">\n'
                for trigger in triggers_vars["lower_triggers"]:
                    output_html += '          <div class="trigger">\n'
                    match trigger:
                        case 'lt1':
                            print("trigger (lt1):", str(triggers_vars['lower_triggers']['lt1']))
                            output_html += (f"            <h4>-LT1:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'lt2':
                            print("trigger (lt2):", str(triggers_vars['lower_triggers']['lt2']))
                            output_html += (f"            <h4>-LT2:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'lt3':
                            print("trigger (lt3):", str(triggers_vars['lower_triggers']['lt3']))
                            output_html += (f"            <h4>-LT3:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                    output_html += '          </div>\n'
                output_html += ("        </div>\n"
                                + "        <br>\n")
            case "upper_triggers":
                output_html += '        <div class="upper-triggers">\n'
                for trigger in triggers_vars["upper_triggers"]:
                    output_html += '          <div class="trigger">\n'
                    match trigger:
                        case 'ut1':
                            print("trigger (ut1):", str(triggers_vars['upper_triggers']['ut1']))
                            output_html += (f"          <h4>+UT1:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'ut2':
                            print("trigger (ut2):", str(triggers_vars['upper_triggers']['ut2']))
                            output_html += (f"          <h4>+UT2:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'ut3':
                            print("trigger (ut3):", str(triggers_vars['upper_triggers']['ut3']))
                            output_html += (f"          <h4>+UT3:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                    output_html += '          </div>\n'
                output_html += "        </div>\n"

    return output_html


def render_event_html(title, time, time_et, symbol, triggers):
    template = env.get_template('reports/template/event-template.html')
    output_html = template.render({
        "title": title,
        "time": time,
        "time_et": time_et,
        "symbol": symbol,
        "triggers": render_triggers_html(triggers)
    })
    return output_html


def render_markdown(template_vars):

    current_date = datetime.datetime.now().strftime("%Y/%m/%d")


    output = f"""
    # {template_vars['year']} Week {template_vars['week_no']} Schedule
    
    ### This was generated on {current_date} and has events from **{template_vars['start_date']}** to **{template_vars['end_date']}**
    
    --------
    
    ## Sunday
    
    {template_vars['sunday_events']}
    
    ## Monday
    
    {template_vars['monday_events']}
    
    ## Tuesday
    
    {template_vars['tuesday_events']}
    
    ## Wednesday
    
    {template_vars['wednesday_events']}
    
    ## Thursday
    
    {template_vars['thursday_events']}
    
    ## Friday
    
    {template_vars['friday_events']}
    """

    return output



    pass

def generate_weekly_schedule(template_vars):
    template = env.get_template('reports/template/weekly-schedule.html')
    output_html = template.render(template_vars)
    output_markdown = render_markdown(template_vars)
    week_no = "15"  # template_vars['week_no']

    """
    file = open(f'new-schedule.md', 'w')
    file.write(output_markdown)
    file.close()
    """
    print("Writing markdown file")
    with open(f'new-schedule.md', 'w') as file:
        file.write(output_markdown)
    print("Markdown file written")

    HTML(string=output_html).write_pdf("reports/weekly-schedules/test_2023-03-30.pdf",
                                       stylesheets=["reports/template/weekly-schedule-style.css"])

triggers_vars = {
    "lta": "Buy",
    "uta": "Sell",
    "lower_triggers": {
        "lt3": {
            "dev": "-3",
            "lots_per_1000": "3",
            "lots": "3"
        },
        "lt2": {
            "dev": "-2",
            "lots_per_1000": "2",
            "lots": "2"
        },
        "lt1": {
            "dev": "-1",
            "lots_per_1000": "1",
            "lots": "1"
        }
    },
    "upper_triggers": {
        "ut1": {
            "dev": "1",
            "lots_per_1000": "1",
            "lots": "1"
        },
        "ut2": {
            "dev": "2",
            "lots_per_1000": "2",
            "lots": "2"
        },
        "ut3": {
            "dev": "3",
            "lots_per_1000": "3",
            "lots": "3"
        }
    }
}

triggers_vars_2 = {
    "lta": "Buy",
    "uta": "Sell",
    "lower_triggers": {
        "lt2": {
            "dev": "-2",
            "lots_per_1000": "2",
            "lots": "2"
        },
        "lt1": {
            "dev": "-1",
            "lots_per_1000": "1",
            "lots": "1"
        }
    },
    "upper_triggers": {
        "ut1": {
            "dev": "1",
            "lots_per_1000": "1",
            "lots": "1"
        },
        "ut2": {
            "dev": "2",
            "lots_per_1000": "2",
            "lots": "2"
        }
    }
}

output_html = """
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
</head>
<body>
    <h1>2023 Week 11 Schedule</h1>
    <p>17 events to trade from 2023/03/14 to 2023/03/14</p>
    <hr>
    <div>
        
    </div>
    <div>
        
    </div>
    <div>
          <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Consumer Price Index (CPI) YoY</h3>
      <h3>Tuesday 14/3 @12:30 (GMT)</h3>
      <h3>Tuesday 14/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Consumer Price Index (CPI) MoM</h3>
      <h3>Tuesday 14/3 @12:30 (GMT)</h3>
      <h3>Tuesday 14/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Consumer Price Index (CPI) Index</h3>
      <h3>Tuesday 14/3 @12:30 (GMT)</h3>
      <h3>Tuesday 14/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.15</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>dev: <span>-0.25</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.15</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT3:</h4>
            <h5>dev: <span>0.25</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Consumer Price Index (CPI) Index, n.s.a.</h3>
      <h3>Tuesday 14/3 @12:30 (GMT)</h3>
      <h3>Tuesday 14/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT3:</h4>
            <h5>dev: <span>-0.4</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT3:</h4>
            <h5>dev: <span>0.4</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>Canada Manufacturing Sales MoM</h3>
      <h3>Tuesday 14/3 @12:30 (GMT)</h3>
      <h3>Tuesday 14/3 @07:30 (ET)</h3>
      <h3>USDCAD</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.7</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.7</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>
    </div>
    <div>
          <div class="card-wrapper">
    <div class="card">
      <h3>Sweden Consumer Price Index (CPI) MoM</h3>
      <h3>Wednesday 15/3 @07:00 (GMT)</h3>
      <h3>Wednesday 15/3 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>Sweden Consumer Price Index (CPI) YoY</h3>
      <h3>Wednesday 15/3 @07:00 (GMT)</h3>
      <h3>Wednesday 15/3 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>Sweden Consumer Price Index at Constant Interest Rates (CPIF) YoY</h3>
      <h3>Wednesday 15/3 @07:00 (GMT)</h3>
      <h3>Wednesday 15/3 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.1</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.1</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>Sweden Consumer Price Index at Constant Interest Rates (CPIF) MoM</h3>
      <h3>Wednesday 15/3 @07:00 (GMT)</h3>
      <h3>Wednesday 15/3 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Buy</span></h4>
        <h4>UTA: <span>Sell</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>1</span></h5>
            <h5>lots: <span>1.0</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Producer Price Index (PPI) MoM</h3>
      <h3>Wednesday 15/3 @12:30 (GMT)</h3>
      <h3>Wednesday 15/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Producer Price Index (PPI) YoY</h3>
      <h3>Wednesday 15/3 @12:30 (GMT)</h3>
      <h3>Wednesday 15/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Core Retail Sales MoM</h3>
      <h3>Wednesday 15/3 @12:30 (GMT)</h3>
      <h3>Wednesday 15/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Producer Price Index (PPI) MoM</h3>
      <h3>Wednesday 15/3 @12:30 (GMT)</h3>
      <h3>Wednesday 15/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Retail Sales MoM</h3>
      <h3>Wednesday 15/3 @12:30 (GMT)</h3>
      <h3>Wednesday 15/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.3</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-0.9</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.3</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>0.9</span></h5>
            <h5>lots/€1k: <span>0.75</span></h5>
            <h5>lots: <span>0.75</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>
    </div>
    <div>
          <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Housing Starts MoM</h3>
      <h3>Thursday 16/3 @12:30 (GMT)</h3>
      <h3>Thursday 16/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-3.0</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
            <h4>-LT2:</h4>
            <h5>dev: <span>-6.0</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>3.0</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
          <div class="trigger">
          <h4>+UT2:</h4>
            <h5>dev: <span>6.0</span></h5>
            <h5>lots/€1k: <span>1.5</span></h5>
            <h5>lots: <span>1.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>  <div class="card-wrapper">
    <div class="card">
      <h3>U.S. Housing Starts</h3>
      <h3>Thursday 16/3 @12:30 (GMT)</h3>
      <h3>Thursday 16/3 @07:30 (ET)</h3>
      <h3>USDJPY</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
        </div>
        <br>
        <div class="upper-triggers">
        </div>

      </div>
    </div>
  </div>
    </div>
    <div>
          <div class="card-wrapper">
    <div class="card">
      <h3>Sweden Unemployment Rate</h3>
      <h3>Friday 17/3 @07:00 (GMT)</h3>
      <h3>Friday 17/3 @02:00 (ET)</h3>
      <h3>USDSEK</h3>
      <hr>
      <div class="triggers">
        <h4>LTA: <span>Sell</span></h4>
        <h4>UTA: <span>Buy</span></h4>
        <br>
          <div class="lower-triggers">
          <div class="trigger">
            <h4>-LT1:</h4>
            <h5>dev: <span>-0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>
        <br>
        <div class="upper-triggers">
          <div class="trigger">
          <h4>+UT1:</h4>
            <h5>dev: <span>0.2</span></h5>
            <h5>lots/€1k: <span>0.5</span></h5>
            <h5>lots: <span>0.5</span></h5>
          </div>
        </div>

      </div>
    </div>
  </div>
    </div>
</body>
"""

# HTML(string=output_html).write_pdf("reports/weekly-schedules/test.pdf",
#                                        stylesheets=["reports/template/weekly-schedule-style.css"])
