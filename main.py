import dash
from dash import html, dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State, ALL
import networkx as nx
import json
import uuid

from classes import GraphManager, RuleManager, main_graph
from layout import create_layout
from callbacks.main_graph import register_main_graph_callbacks
from callbacks.rule import register_rule_callbacks
from callbacks.rule_creation_graphs import register_rule_creation_graphs_callbacks

app = dash.Dash(__name__)

app.layout = create_layout()

register_main_graph_callbacks(app)
register_rule_callbacks(app)
register_rule_creation_graphs_callbacks(app)


if __name__ == '__main__':
    app.run_server(debug=True)
