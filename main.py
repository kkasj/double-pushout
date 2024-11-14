import dash
from utils.file_operations import load_rules_from_directory

from layout import create_layout
from callbacks.main_graph import register_main_graph_callbacks
from callbacks.rule import register_rule_callbacks
from callbacks.rule_creation_graphs import register_rule_creation_graphs_callbacks

def create_app():
    app = dash.Dash(__name__)
    
    app.layout = create_layout()
    
    register_main_graph_callbacks(app)
    register_rule_callbacks(app)
    register_rule_creation_graphs_callbacks(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)
