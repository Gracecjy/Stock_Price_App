
# coding: utf-8


#import packages 
import numpy as np
import pandas as pd
import bokeh
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.embed import components
from flask import Flask, render_template, request, redirect
import requests
bv = bokeh.__version__



#create flask instance
app = Flask(__name__)
app.vars={}
selection = ['Open', 'Adj. Open', 'Close', 'Adj. Close']



@app.route('/')
def main():
    return redirect('/index')


@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        app.vars['ticker'] = request.form['ticker'].upper()
        app.vars['select'] = [selection[i] for i in range(4) if selection[i] in request.form.values()]
        return redirect('/graph')



@app.route('/graph', methods=['GET', 'POST'])
def graph():
    # request data from quandl.com and generate pandas dataframe
    url = 'https://www.quandl.com/api/v3/datasets/WIKI/'
    url += '{}.json?'.format(app.vars['ticker'])
    url += 'start_date=2017-09-01&end_date=2017-09-30&api_key=B69idyhVfSZV5yq7r6nc'
    data = requests.get(url).json()['dataset']
    col_name = data['column_names']
    df = pd.DataFrame(np.array(data['data']), columns=col_name)
    df = df[['Date', 'Open', 'Adj. Open', 'Close', 'Adj. Close']]
    df[['Open', 'Adj. Open', 'Close', 'Adj. Close']] = df[[
        'Open', 'Adj. Open', 'Close', 'Adj. Close']].astype(float)
    df['Date'] = pd.to_datetime(df['Date'])

    # generate bokeh plot
    p = figure(plot_width=500, plot_height=500,
               title="Stock Price for {} (09/01/2017 - 09/30/2017)".format(app.vars['ticker']), x_axis_type="datetime")

    if 'Open' in app.vars['select']:
        p.line(df['Date'], df['Open'], line_width=3,
               line_color="#658b33", legend='Open')
    if 'Adj. Open' in app.vars['select']:
        p.line(df['Date'], df['Adj. Open'], line_width=3,
               line_color="#949150", legend='Adjusted Open')
    if 'Close' in app.vars['select']:
        p.line(df['Date'], df['Close'], line_width=3,
               line_color="#dbc69d", legend='Close')
    if 'Adj. Close' in app.vars['select']:
        p.line(df['Date'], df['Adj. Close'], line_width=3,
               line_color="#d29fa2", legend='Adjusted Close')

    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Price"
    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_style = 'bold'
    p.xaxis.bounds = (df.Date.iloc[-1], df.Date.iloc[0])

    script, div = components(p)
    return render_template('graph.html', bv=bv, ticker=app.vars['ticker'], script=script, div=div)



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)





