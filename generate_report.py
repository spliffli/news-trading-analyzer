import datetime

from analyze_data import read_news_data, read_triggers, load_news_pip_data, calc_news_pip_metrics, \
    news_pip_metrics_to_dfs
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from utils import str_to_datetime
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


def generate_report(haawks_id_str, symbol, news_data, news_pip_metrics_dfs, triggers, symbol_higher_dev, indicator_info):
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
    output_html = (f"            <h5>dev: <span>{trigger['dev']}</span></h5>\n"
                   + f"            <h5>lots/$1000: <span>{trigger['lots_per_1000']}</span></h5>\n"
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
                            output_html += (f"            <h4>-LT1:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'lt2':
                            output_html += (f"            <h4>-LT2:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'lt3':
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
                            output_html += (f"          <h4>+UT1:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'ut2':
                            output_html += (f"          <h4>+UT2:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                        case 'ut3':
                            output_html += (f"          <h4>+UT3:</h4>\n"
                                            + render_trigger_html(triggers_vars[key][trigger]))
                    output_html += '          </div>\n'
                output_html += "        </div>\n"

    return output_html


def render_event_html(title, time, symbol, triggers):
    template = env.get_template('reports/template/event-template.html')
    output_html = template.render({
        "title": title,
        "time": time,
        "symbol": symbol,
        "triggers": render_triggers_html(triggers)
    })
    return output_html


def generate_weekly_schedule():
    pass

triggers_vars = {
    "lta": "Buy",
    "uta": "Sell",
    "lower_triggers": {
        "lt1": {
            "dev": "-1",
            "lots_per_1000": "1",
            "lots": "1"
        },
        "lt2": {
            "dev": "-2",
            "lots_per_1000": "2",
            "lots": "2"
        },
        "lt3": {
            "dev": "-3",
            "lots_per_1000": "3",
            "lots": "3"
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

output_html = render_event_html("Canada Employment Change MoM", datetime.time(15, 30), "USDCAD", triggers_vars_2)
