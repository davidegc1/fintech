import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import (
    Dash,
    html,
    dcc,
    Output,
    Input,
    callback_context
)

from graph_functions import (
    plot_monthly_credit_debit_line,
    plot_spending_by_category_pie
)

# Load and preprocess data
df = pd.read_csv("movements.csv", parse_dates=["timestamp"])
df["timestamp"] = df["timestamp"].dt.tz_localize(None)  # Ensure tz-naive

# Initialize Dash app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Plotly table generator
def create_plotly_table(dataframe):
    if dataframe.empty:
        return go.Figure(layout={"title": "No transactions found"})

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(dataframe.columns),
            fill_color='lightgray',
            align='left',
            font=dict(size=12, color='black')
        ),
        cells=dict(
            values=[dataframe[col] for col in dataframe.columns],
            fill_color='white',
            align='left',
            font=dict(size=11)
        )
    )])
    fig.update_layout(title="Transactions", height=400)
    return fig

# App layout
app.layout = html.Div(children=[
    html.H1("Personal Finance App", style={'textAlign': 'center', "fontSize": 30}),

    # Filters
    html.Div(className='row', children=[
        html.Div(className='four columns', children=[
            html.Label("Date Range"),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=df['timestamp'].min().date(),
                max_date_allowed=df['timestamp'].max().date(),
                start_date=df['timestamp'].min().date(),
                end_date=df['timestamp'].max().date()
            )
        ]),
        html.Div(className='four columns', children=[
            html.Label("Categories"),
            dcc.Checklist(
                id='category-selector',
                options=[{'label': cat, 'value': cat} for cat in sorted(df['category'].unique())],
                value=[],
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            )
        ]),
        html.Div(className='four columns', children=[
            html.Label("Granularity"),
            dcc.Dropdown(
                id='granularity-selector',
                options=[
                    {'label': 'Daily', 'value': 'D'},
                    {'label': 'Weekly', 'value': 'W'},
                    {'label': 'Monthly', 'value': 'M'}
                ],
                value='M',
                clearable=False
            )
        ])
    ], style={'marginBottom': 30}),

    # Charts
    html.Div(className="row", children=[
        html.Div(className="six columns", children=[
            dcc.Graph(id="line-chart")
        ]),
        html.Div(className="six columns", children=[
            dcc.Graph(id="pie-chart")
        ]),
    ]),

    # Type filter + Plotly table
    html.Div(className="row", children=[
        html.Div(className="twelve columns", children=[
            html.Div([
                html.Label("Type:", style={'marginRight': '10px'}),
                dcc.RadioItems(
                    id='type-selector',
                    options=[
                        {'label': 'All', 'value': 'all'},
                        {'label': 'Credit', 'value': 'credit'},
                        {'label': 'Debit', 'value': 'debit'}
                    ],
                    value='all',
                    labelStyle={'display': 'inline-block', 'marginRight': '15px'},
                    inputStyle={"marginRight": "5px"}
                )
            ], style={'display': 'flex', 'justifyContent': 'flex-end', 'marginRight': '30px', 'marginBottom': '10px'}),

            dcc.Graph(id="plotly-table")
        ])
    ])
])

# Callback for interactivity
@app.callback(
    Output('line-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Output('plotly-table', 'figure'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('category-selector', 'value'),
    Input('pie-chart', 'clickData'),
    Input('type-selector', 'value'),
    Input('granularity-selector', 'value')
)
def update_components(start_date, end_date, selected_categories, pie_click, selected_type, granularity):
    # Prepare dates
    start = pd.to_datetime(start_date).tz_localize(None)
    end = pd.to_datetime(end_date).tz_localize(None)

    df_local = df.copy()
    df_local["timestamp"] = df_local["timestamp"].dt.tz_localize(None)

    # Filter by date
    dff = df_local[(df_local['timestamp'] >= start) & (df_local['timestamp'] <= end)]

    # Determine interaction source
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # If pie chart clicked, override type to "debit" and category to selected slice
    if triggered_id == "pie-chart" and pie_click:
        dff = dff[dff["type"] == "debit"]
        pie_category = pie_click['points'][0]['label']
        dff = dff[dff["category"] == pie_category]
    else:
        # Filter by type from radio button
        if selected_type != "all":
            dff = dff[dff["type"] == selected_type]
        # Filter by category list
        if selected_categories:
            dff = dff[dff["category"].isin(selected_categories)]

    # Generate visuals
    line_fig = plot_monthly_credit_debit_line(dff, granularity)
    pie_fig = plot_spending_by_category_pie(dff)
    table_fig = create_plotly_table(dff)

    return line_fig, pie_fig, table_fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)