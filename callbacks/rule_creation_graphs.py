import dash
from dash.dependencies import Input, Output, State, ALL

from classes import GraphManager, RuleManager

def register_rule_creation_graphs_callbacks(app):
    @app.callback(
        [Output('lhs-graph', 'elements', allow_duplicate=True),
        Output('rhs-graph', 'elements', allow_duplicate=True)],
        Input('current-rule', 'data'),
        prevent_initial_call=True
    )
    def update_graphs_from_rule_data(current_rule_data):
        print("update_graphs_from_rule_data callback triggered")
        current_rule = RuleManager.from_dict(current_rule_data)
        current_rule.highlight_k_elements()
        return current_rule.lhs.elements, current_rule.rhs.elements

    @app.callback(
        Output('current-rule', 'data', allow_duplicate=True),
        [Input('add-lhs-node-button', 'n_clicks'),
        Input('add-lhs-edge-button', 'n_clicks'),
        Input('remove-lhs-selected-button', 'n_clicks')],
        [State('current-rule', 'data'),
        State('lhs-graph', 'selectedNodeData'),
        State('lhs-graph', 'selectedEdgeData')],
        prevent_initial_call=True
    )
    def modify_rule_from_lhs_graph(n_clicks_add_node, n_clicks_add_edge, n_clicks_remove, 
                        current_rule_data, selected_nodes, selected_edges):
        print("modify_rule_from_lhs_graph callback triggered")
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        current_rule = RuleManager.from_dict(current_rule_data)
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'add-lhs-node-button':
            node_id = f"lhs_{len(current_rule.lhs.elements) + 1}"
            current_rule.lhs.add_node(node_id)
            current_rule.rhs.add_node(node_id)
        elif trigger_id == 'add-lhs-edge-button':
            if selected_nodes and len(selected_nodes) >= 2:
                for i in range(len(selected_nodes)):
                    for j in range(i + 1, len(selected_nodes)):
                        source, target = selected_nodes[i]['id'], selected_nodes[j]['id']
                        current_rule.lhs.add_edge(source, target)
                        current_rule.rhs.add_edge(source, target)
        elif trigger_id == 'remove-lhs-selected-button':
            k_elements = current_rule_data.get('k', {}) if current_rule_data else {}
            current_rule.lhs.remove_elements(selected_nodes, selected_edges, k_elements)
            current_rule.rhs.remove_elements(selected_nodes, selected_edges, k_elements)

        return current_rule.to_dict()

    @app.callback(
        Output('current-rule', 'data', allow_duplicate=True),
        [Input('add-rhs-node-button', 'n_clicks'),
        Input('add-rhs-edge-button', 'n_clicks'),
        Input('remove-rhs-selected-button', 'n_clicks')],
        [State('current-rule', 'data'),
        State('rhs-graph', 'selectedNodeData'),
        State('rhs-graph', 'selectedEdgeData')],
        prevent_initial_call=True
    )
    def modify_rule_from_rhs_graph(n_clicks_add_node, n_clicks_add_edge, n_clicks_remove, current_rule_data, selected_nodes, selected_edges):
        print("modify_rule_from_rhs_graph callback triggered")
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        current_rule = RuleManager.from_dict(current_rule_data)
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'add-rhs-node-button':
            node_id = f"rhs_{len(current_rule.rhs.elements) + 1}"
            current_rule.rhs.add_node(node_id)
        elif trigger_id == 'add-rhs-edge-button':
            if selected_nodes and len(selected_nodes) >= 2:
                for i in range(len(selected_nodes)):
                    for j in range(i + 1, len(selected_nodes)):
                        source, target = selected_nodes[i]['id'], selected_nodes[j]['id']
                        current_rule.rhs.add_edge(source, target)
        elif trigger_id == 'remove-rhs-selected-button':
            k_elements = current_rule_data.get('k', {}) if current_rule_data else {}
            print(current_rule.rhs.graph.nodes())
            print(current_rule.rhs.graph.edges())
            current_rule.rhs.remove_elements(selected_nodes, selected_edges, k_elements)

        return current_rule.to_dict()