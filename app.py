from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure
from bokeh.io import output_notebook, show
from bokeh.resources import CDN
from bokeh.embed import file_html, json_item, components
import simplejson as json
import requests
import pandas as pd

app = Flask(__name__)

def get_data(ticker_code):
    response = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker_code}&apikey=O2S1THRBR0HS4O8I')
    if response.status_code == 200 and len(response.json())>1:
        data = pd.DataFrame(response.json()['Time Series (Daily)']).T
        data.index = pd.to_datetime(data.index)
        data = data.rename(columns={'1. open': 'opening', '4. close': 'closing', '5. adjusted close': 'closing_a'})
        return data[['opening', 'closing', 'closing_a']]
    else:
        return 0

def make_plot(parameters):
    legend_names = {'closing':'Closing', 'closing_a':'Closing (adjusted)', 'opening':'Opening'}
    error = False
    plot = figure(x_axis_type='datetime', title = 'Price over the last 100 days')

    if 'ticker_code' in parameters.keys():
        data = get_data(parameters['ticker_code'])
        if type(data) == int:
            error = True
        
        else:
            requested_prices = set(parameters.keys()) - {'ticker_code'}
            if len(requested_prices) == 0:
                error = True
            else:
                for price_type, color in zip(requested_prices, {'red','green','blue'}):
                    plot.line(data.index.values, data[price_type].values.astype('float'), color=color, line_width=3, legend_label = legend_names[price_type])
                plot.xaxis.axis_label = 'Date'
                plot.yaxis.axis_label = 'Price ($)'
                plot.legend.location = 'top_left'
                plot.legend.click_policy = 'hide'
    else:
        error = True
        
    if error:
        return 0
    else:
        return plot
    
    
@app.route('/')
def index():
    return render_template('form.html', outside_title='This is a title!')

@app.route('/form_action', methods=['GET', 'POST'])
def form_action():
    form_results = request.form.to_dict()
    print(form_results)
    plot = make_plot(form_results)
    if plot == 0:
        return render_template('graph.html', input_text="An error occured!", open_div = "Please double-check that the code you entered is valid.")
    else:
        script, div = components(plot)
        return render_template('graph.html', input_text=f"Here is the info for {form_results['ticker_code']}", open_div = div, plot_script = script )

if __name__ == '__main__':
    app.run(port=33507)
