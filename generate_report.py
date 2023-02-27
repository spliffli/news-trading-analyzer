from analyze_data import read_news_data, read_triggers, load_news_pip_data, calc_news_pip_metrics, \
    news_pip_metrics_to_dfs
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from utils import str_to_datetime
import pandas as pd

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('reports/template/report-template.html')

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
