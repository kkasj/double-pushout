import dash
from dash.dependencies import Input, Output, State, ALL

from classes import GraphManager
from utils import get_default_graph_layout

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
        Output('main-graph', 'layout'),
        Input('reset-view-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_graph_view(n_clicks):
        ctx = dash.callback_context
        if ctx.triggered:
            return get_default_graph_layout()
        return dash.no_update