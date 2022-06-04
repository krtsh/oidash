import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import time
import dash_bootstrap_components as dbc
from all_classes import Authentication, DataDownload

# <--------------------------------------------------------------------------------------------->

today = date.today()
auth = Authentication.auth('krtsh@icloud.com', '2538738')
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server
app.config.suppress_callback_exceptions = True
# <--------------------------------------------------------------------------------------------->

head = html.Div(
    [
        html.Center('INTRADAY MOEX OPEN INTEREST')
    ], style={'color': 'white', 'fontSize': 25})

popover_children = [
    dbc.PopoverHeader("Онлайн индикатор открытого интереса по лицам"),
    dbc.PopoverBody("Используются данные Московской биржи - https://www.moex.com/ru/analyticalproducts?futoi"),
]

buttons = html.Div(
    [
        dbc.Button('SBER', id='sr', size='lg', style={"width": "100px"}),
        dbc.Button('GAZP', id='gz', size='lg', style={"width": "100px"}),
        dbc.Button('SI', id='si', size='lg', style={"width": "100px"}),
        dbc.Button('RTS', id='ri', size='lg', style={"width": "100px"}),
        dbc.Button('BRENT', id='br', size='lg', style={"width": "100px"}),
        dbc.Button("About", id="click-target", color="danger", className="mr-1"),
        dbc.Popover(popover_children, id="click", target="click-target", trigger="click", placement="bottom"),
        html.Div(id="content")
    ], className="p-1 d-flex justify-content-center"
)
date_picker = html.Div(
    [
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=date(2020, 5, 12),
            max_date_allowed=date(2030, 1, 1),
            initial_visible_month=today,
            start_date=today,
            end_date=today
        ),
        html.Div(id='output-container-date-picker-range')
    ], className="p-1 d-flex justify-content-center"
)
graph = html.Div(
    [
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 10000,  # in milliseconds
            n_intervals=0),
    ], className="d-flex justify-content-left"
)
picker_buttons = dbc.FormGroup(
    [
        date_picker,
        buttons
    ], className='form-row'
)

# <--------------------------------------------------------------------------------------------->

app.layout = html.Div(
    [
        dcc.Store(id='local', storage_type='local'),
        dbc.Container(
            head,
            className='d-flex justify-content-center',
        ),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            picker_buttons
                        )
                    )
                ]
            ),
            className='d-flex justify-content-center',
            style={'max-width': '100%'}
        ),
        dbc.Container(
            graph,
            className='row align-items-start',
        )
    ], style={'background-color': '#272b30'}
)

# <--------------------------------------------------------------------------------------------->


@app.callback(
    Output('local', 'data'),
    Input('sr', 'n_clicks'),
    Input('gz', 'n_clicks'),
    Input('si', 'n_clicks'),
    Input('ri', 'n_clicks'),
    Input('br', 'n_clicks'),
)
def push_button(sr, gz, si, ri, br):
    ctx = dash.callback_context

    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return button_id


@app.callback(
    Output('live-update-graph', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('local', 'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_graph_live(n_intervals, sec, start_date, end_date):

    if time.localtime()[3:5] == (23, 59):
        global today
        today = date.today()

    df = DataDownload.go_data(sec, start_date, end_date, auth[0], auth[1])

    fig = make_subplots(rows=3, cols=2, vertical_spacing=0.06, horizontal_spacing=0.035,
                        subplot_titles=("LONG YUR", "LONG FIZ", "SHORT YUR", "SHORT FIZ", "POS YUR", "POS FIZ"),

                        )
    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "YUR"').tradedate,
        y=df.query('clgroup == "YUR"').pos_long,
        name=f"long yur {sec}",
        mode='lines+markers+text',
        marker={'color': 'green'},
    ), 1, 1)

    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "YUR"').tradedate,
        y=df.query('clgroup == "YUR"').pos_short,
        name=f"short yur {sec}",
        mode='lines+markers+text',
        marker={'color': 'red'}

    ), 2, 1)

    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "YUR"').tradedate,
        y=df.query('clgroup == "YUR"').pos_long_num,
        name=f"long pos yur {sec}",
        mode='lines+markers+text',
        marker={'color': 'green'}
    ), 3, 1)

    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "YUR"').tradedate,
        y=df.query('clgroup == "YUR"').pos_short_num,
        name=f"short pos yur {sec}",
        mode='lines+markers+text',
        marker={'color': 'red'}
    ), 3, 1)

    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "FIZ"').tradedate,
        y=df.query('clgroup == "FIZ"').pos_long,
        name=f"long fiz {sec}",
        mode='lines+markers+text',
        marker={'color': 'green'}
    ), 1, 2)

    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "FIZ"').tradedate,
        y=df.query('clgroup == "FIZ"').pos_short,
        name=f"short fiz {sec}",
        mode='lines+markers+text',
        marker={'color': 'red'}
    ), 2, 2)

    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "FIZ"').tradedate,
        y=df.query('clgroup == "FIZ"').pos_long_num,
        name=f"long pos fiz {sec}",
        mode='lines+markers+text',
        marker={'color': 'green'}
    ), 3, 2)

    fig.append_trace(go.Scatter(
        x=df.query('clgroup == "FIZ"').tradedate,
        y=df.query('clgroup == "FIZ"').pos_short_num,
        name=f"short pos fiz {sec}",
        mode='lines+markers+text',
        marker={'color': 'red'},
    ), 3, 2)

    fig.update_layout(width=1920, height=900, showlegend=False, paper_bgcolor='#3C4247',
                      margin=dict(t=25, l=10, r=15, b=0), font_color="white")
    fig.update_xaxes(tickfont=dict(color='white'), showline=True, linewidth=1,
                     linecolor='black', mirror=True, gridcolor='#E0E0E0')
    fig.update_yaxes(tickfont=dict(color='white'), showline=True, linewidth=1,
                     linecolor='black', mirror=True, gridcolor='#E0E0E0', side='right')
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=[00, 7], pattern="hour"),
            dict(bounds=['sat', 'mon'])
        ]
    )
    return fig

# <--------------------------------------------------------------------------------------------->


if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
