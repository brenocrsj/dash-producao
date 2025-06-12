# components/tabs_layout.py
from dash import dcc, html

def create_tabs():
    return dcc.Tabs(id="tabs-main", value='tab-graphs', className="custom-tabs", children=[
        dcc.Tab(label='Dashboard Gráfico', value='tab-graphs', className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div(id='tab-content-graphs', className="tab-content")
        ]),
        dcc.Tab(label='Análise Matricial', value='tab-matrix', className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div(id='tab-content-matrix', className="tab-content")
        ]),
        dcc.Tab(label='Análise de Eficiência', value='tab-efficiency', className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div(id='tab-content-efficiency', className="tab-content")
        ]),
    ])