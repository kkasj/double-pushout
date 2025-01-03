import dash
from dash.dependencies import Input, Output, State, ALL
from datetime import datetime
import json
import base64

from classes import GraphManager
from utils.layout import get_default_graph_layout
from utils.file_operations import save_graph_to_file

def register_main_graph_callbacks(app):
    @app.callback(
        Output('main-graph', 'elements'),
        [Input('add-node-button', 'n_clicks'),
        Input('add-edge-button', 'n_clicks'),
        Input('remove-selected-button', 'n_clicks')],
        [State('main-graph', 'elements'),
        State('main-graph', 'selectedNodeData'),
        State('main-graph', 'selectedEdgeData')]
    )
    def update_graph(n_clicks_node, n_clicks_edge, n_clicks_remove, elements, selected_nodes, selected_edges):
        print("update_graph callback triggered")
        ctx = dash.callback_context
        if not ctx.triggered:
            return elements
        
        main_graph = GraphManager.from_elements(elements)
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'add-node-button':
            node_id = str(len([element for element in main_graph.elements if 'source' not in element['data']]) + 1)
            main_graph.add_node(node_id)
        elif button_id == 'add-edge-button':
            if selected_nodes and len(selected_nodes) >= 2:
                for i in range(len(selected_nodes)):
                    for j in range(i + 1, len(selected_nodes)):
                        source, target = selected_nodes[i]['id'], selected_nodes[j]['id']
                        main_graph.add_edge(source, target)
        elif button_id == 'remove-selected-button':
            main_graph.remove_elements(selected_nodes, selected_edges)
        
        return main_graph.elements
    
    @app.callback(
        Output('main-graph', 'layout', allow_duplicate=True),
        Input('reset-view-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_graph_view(n_clicks):
        ctx = dash.callback_context
        if ctx.triggered:
            return get_default_graph_layout()
        return dash.no_update
    
    @app.callback(
        Output('save-graph-button', 'n_clicks', allow_duplicate=True),
        Input('save-graph-button', 'n_clicks'),
        State('main-graph', 'elements'),
        prevent_initial_call=True
    )
    def save_graph(n_clicks, elements):
        if n_clicks > 0:
            graph_data = {
                'elements': elements,
                'timestamp': datetime.now().isoformat()
            }
            filepath = save_graph_to_file(graph_data)
            print(f"Graph saved to: {filepath}")
        return 0  # Reset n_clicks
    
    # @app.callback(
    #     Output('graph-upload', 'contents'),
    #     Input('load-graph-button', 'n_clicks'),
    #     prevent_initial_call=True
    # )
    # def trigger_upload(n_clicks):
    #     if n_clicks:
    #         # Return an empty string to trigger the upload dialog
    #         return ''
    #     return dash.no_update
    
    @app.callback(
        Output('main-graph', 'elements', allow_duplicate=True),
        Input('graph-upload', 'contents'),
        prevent_initial_call=True
    )
    def load_graph(contents):
        if contents is None:
            return dash.no_update
        
        try:
            # Remove the data URL prefix (e.g., "data:application/json;base64,")
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            graph_data = json.loads(decoded)
            
            # Create a GraphManager instance to validate the data
            graph_manager = GraphManager.from_dict(graph_data)
            return graph_manager.elements
            
        except Exception as e:
            print(f'Error loading graph: {e}')
            return dash.no_update