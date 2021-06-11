import dash
import dash_table as dt
import pandas as pd
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import dash_auth as da
import auth

#
# # Create an ID column to use it to add behaviour
df = pd.read_csv("Test.csv")
# # print(df.columns)
# df["id"] = df["TotalPop"]
# df.set_index("id", inplace=True, drop=False)
# # print(df.columns)
# # breakpoint()
# # exit()

app = dash.Dash(__name__)

server = app.server

da.BasicAuth(app, auth.approve())
# auth.approve()
# exit()
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([html.H2("Main Demo")], className="text-center text-success")]),
    dbc.Row([
        dbc.Col([html.H4("qen"), html.Hr(), dbc.CardHeader(dbc.Button("Show Contents 1", color="link", id="button_12")),
                 dbc.Collapse(dbc.CardBody("inside contents 1"), id="collapse_12"), html.Hr(),
                 dbc.CardHeader(dbc.Button("Show contents 2", color="link", id="button_13")), html.Hr(),
                 dbc.Collapse(dbc.CardBody("inside contents 2"), id="collapse_13")], width=4),
        dbc.Col([html.H3("Test"), dcc.Graph(id="graph2")], width=7)]),
    dbc.Row([
        dbc.Col([dt.DataTable(id="d1", columns=[{"name": i, "id": i, "deletable": True, "selectable": True,
                                                 "hideable": True} if i == "TotalPop" or i == "id"
                                                                      or i == "income" or i == "Unemployment" else {
            "name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns],
                              data=df.to_dict('records'),
                              editable=True,
                              filter_action="native",
                              sort_action="native",
                              sort_mode="multi",
                              column_selectable="single",
                              row_selectable="multi",
                              row_deletable=True,
                              selected_columns=[],
                              selected_rows=[],
                              page_action="native",
                              page_current=0,
                              page_size=10,

                              )])]),

    html.Br(),
    html.Div(id="fig12"),
    dbc.Row([
        dbc.Col([html.H6("Ken"), html.Label("States:", style={"fontSize": 25, "textAlign": "center"}),
                 dcc.Dropdown(id="drop1", options=[{"label": i, "value": i} for i in sorted(df.State.unique())],
                              value="Nevada", clearable=False)], width=3),
        dbc.Col([html.H6("Sen"), html.Label("Counties:", style={"fontSize": 25, "textAlign": "center"}),
                 dcc.Dropdown(id="drop2", multi=True)], width=3),
        dbc.Col([html.H6("Den"), dcc.Graph(id="line_figure2")], width=6)]),
    dbc.Row([
        dbc.Col([dcc.Slider(id="slider1")])]),
    dbc.Row([
        dbc.Col([html.H6("wen"), dcc.Graph(id="line_figure3")]),
        dbc.Col([html.H6("zen"), dcc.Graph(id="line_figure4")])])
])


@app.callback(
    Output('d1', 'style_data_conditional'),
    Input('d1', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(
    Output('fig12', "children"),
    Input('d1', "derived_virtual_data"),
    Input('d1', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["Poverty"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["Citizen", "Unemployment", "Income"] if column in dff
    ]


@app.callback(Output("drop2", "options"),
              Input("drop1", "value"))
def give_drop2data(value):
    """
    :param value:
    :return:
    """
    test = df["State"] == value
    new_df = df[test]
    # print(new)
    tru = [{"label": i, "value": i} for i in sorted(new_df.County.unique())]
    # print(tru)
    return tru


@app.callback(Output("drop2", "value"),
              Input("drop2", "options"))
def print_values(opt):
    fur = [x["value"] for x in opt]
    # print(fur)
    return fur


@app.callback(Output("line_figure2", "figure"),
              [Input("drop1", "value"),
               Input("drop2", "value")])
def update_graph(opl, opp):
    if len(opp) == 0:
        return dash.no_update
    else:
        dff = (df.State == opl) & (df.County.isin(opp))
        new_df = df[dff]
        # print(new_df)
        fig = px.scatter(new_df, x="TotalPop", y="Employed", color="Poverty", trendline="Income",
                         hover_name="ChildPoverty")

        return fig


@app.callback(Output("graph2", "figure"),
              [Input("drop1", "value"),
               Input("drop2", "value")])
def update_graph(opl, opp):
    if len(opp) == 0:
        return dash.no_update
    else:
        dff = (df.State == opl) & (df.County.isin(opp))
        new_df = df[dff].dropna()
        # print(new_df)
        fig = px.line(new_df, x="Income", y="Poverty", color="State", line_group="Women",
                      hover_name="Men")

        return fig


@app.callback(
    Output("collapse_12", "is_open"),
    [Input("button_12", "n_clicks")],
    [State("collapse_12", "is_open")])
def clp(n, y):
    if n:
        return not y
    return y


@app.callback(
    Output("collapse_13", "is_open"),
    [Input("button_13", "n_clicks")],
    [State("collapse_13", "is_open")])
def clp(n, y):
    if n:
        return not y
    return y


if __name__ == "__main__":
    app.run_server(debug=True)
