import dash

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
