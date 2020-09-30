import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html 
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import base64
from flask import Flask
import os

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

##############################
#Data Preparation

df = pd.read_excel("BQ-Assignment-Data-Analytics.xlsx")
#print(df.head())

from datetime import datetime
date = []
for d in df.Date:
     date.append(datetime.strftime(d, '%b %y'))
     
df['Date'] = date

table = pd.pivot_table(df, values='Sales', index=['Item Type', 'Item','Item Sort Order'],
                    columns=['Date'], aggfunc=np.sum)
reshaped_df =  table.rename_axis(None, axis=1).reset_index() 
reshaped_df = reshaped_df.sort_values(by='Item Sort Order',ascending = True)
print (reshaped_df)

##############################
image_filename = 'bq.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div(
    [
        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
        ]),
        html.H2("Interative Output Format: "),
        html.Div([
            html.Div([
                html.H6("Item Type"),
                html.Div([
                dcc.Checklist(id='select-all',
                            options=[
                                {'label': 'Select All', 'value': 1}
                                ],
                                value=[]
                                )],
                            id='checklist-container'
                ),
                dcc.Checklist(
                    id="my-checklist",
                    options=[
                        {"label": i, "value": i} for i in ['Fruit','Vegetable']
                    ],
                    value=[],
                    #labelStyle={"display": "inline-block"},
                )],
            id='checkbox',
            style= {
                'position':'relative',
                'padding':'5px',
                'width':'150px',
                'border':'1px solid black'
            }
            ),
            html.Div([
                dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i, "selectable": True} for i in reshaped_df.iloc[:,1:8].columns
                    ],
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold',
                        'color': 'black',
                        'border': '0px'
                    },
                    style_cell={'textAlign': 'right'},
                    style_table={'height': '400px','width':'900px'},
                    style_cell_conditional = [
                        {
                        'if' : {'column_id': c}, 
                        'textAlign': 'left'
                        } for c in ['Item','Item Sort Order']
                    ],
                    style_data_conditional = [
                        {
                            'if':{'row_index':'odd'},
                            'backgroundColor':'rgb(248,248,248)'
                            
                        },
                        {
                            'if':{'column_id':'Item'},
                            'backgroundColor':'rgb(248,248,248)'
                        }
                    ],
                    data=reshaped_df.iloc[:,1:8].to_dict('records'),
                    sort_action="native",
                    sort_mode="multi",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="native",
                    page_current= 0,
                    page_size= 10,
                ),
                html.Div(id='datatable-interactivity-container')
            ], style={'padding-left':'40px'}),
        ],style = {'width': '100%', 'display': 'flex', 'align-items': 'flex-start', 'justify-content': 'left'}
        ),
    ],style = {'backgroundColor':'#F2F7FA'}
)

@app.callback(
    Output('datatable-interactivity', 'data'),
    [Input('my-checklist', 'value') ] )
def display_table(val):
    print(val)
    dff = reshaped_df[reshaped_df['Item Type'].isin(val)]
    dff = dff.iloc[:,1:8]
    print(dff)
    return dff.to_dict('records')


# @app.callback(
#     Output('datatable-interactivity', 'style_data_conditional'),
#     [Input('datatable-interactivity', 'selected_columns')]
# )
# def update_styles(selected_columns):
#     return [{
#         'if': { 'column_id': i },
#         'background_color': '#D2F3FF'
#     } for i in selected_columns]


# @app.callback(
#     Output("my-checklist", "value"),
#     [Input("all-or-none", "value")],
#     [State("my-checklist", "options")],
# )
# def select_all_none(all_selected, options):
#     all_or_none = []
#     all_or_none = [option["value"] for option in options if all_selected] 
#     return all_or_none

@app.callback(
    Output('my-checklist', 'value'),
    [Input('select-all', 'value')],
    [State('my-checklist', 'options')])
def test(selected, options):
    if len(selected) > 0:
        #print([i['value'] for i in options])
        return [i['value'] for i in options]
    raise PreventUpdate()
    
@app.callback(
    Output('checklist-container', 'children'),
    [Input('my-checklist', 'value')],
    [State('my-checklist', 'options'),
     State('select-all', 'value')])
def tester(selected, options_1, checked):

    if len(selected) < len(options_1) and len(checked) == 0:
        raise PreventUpdate()

    elif len(selected) < len(options_1) and len(checked) == 1:
        return  dcc.Checklist(id='select-all',
                    options=[{'label': 'Select All', 'value': 1}], value=[])

    elif len(selected) == len(options_1) and len(checked) == 1:
        raise PreventUpdate()

    return  dcc.Checklist(id='select-all',
                    options=[{'label': 'Select All', 'value': 1}], value=[1])



if __name__ == '__main__':
    app.run_server(debug=True)