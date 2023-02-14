from analyze_data import read_news_data, read_triggers, load_news_pip_data, calc_news_pip_metrics, news_pip_metrics_to_dfs
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('reports/template/report-template.html')


news_data = read_news_data("10290")
triggers = read_triggers("10290")
news_pip_data = load_news_pip_data("10290", news_data, "USDCAD")
news_pip_metrics = calc_news_pip_metrics(news_pip_data, triggers, higher_dev="bearish")
news_pip_metrics_dfs = news_pip_metrics_to_dfs(news_pip_metrics)

template_vars = {
    "title": "Canada Employment Change",
    "haawks_id": "10290",
    "symbol": "USDCAD",
    "importance": "***",
    "bullish_or_bearish": "bearish",
    "description":
    """
Employment Change measures the change in the number of people employed. Job creation is an important indicator of consumer spending.

A higher than expected reading should be taken as positive/bullish for the CAD, while a lower than expected reading should be taken as negative/bearish for the CAD.""",
    "no_of_releases": "73",
    "start_date": "2017-01-06",
    "end_date": "2023-01-06",
    "data": news_pip_metrics_dfs['trigger_1'].to_html(index=False)
}

html_out = template.render(template_vars)
HTML(string=html_out).write_pdf("report-example.pdf", stylesheets=["reports/template/report-style.css"])