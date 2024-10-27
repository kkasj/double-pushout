
import dash
from dash import html, dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State, ALL
import networkx as nx
import json
import uuid

from classes import GraphManager, RuleManager, main_graph
from layout import create_layout
from utils import match_subgraph

def register_rule_callbacks(app):
    @app.callback(
        [Output('rules-store', 'data', allow_duplicate=True),
        Output('rule-list', 'children', allow_duplicate=True)],
        Input('finalize-rule-button', 'n_clicks'),
        [State('rules-store', 'data'),
        State('current-rule', 'data'),
        State('rule-list', 'children')],
        prevent_initial_call=True
    )
    def finalize_rule(n_clicks, rules, current_rule_data, rule_list_children):
        print("finalize_rule callback triggered")
        if n_clicks > 0:
            rules.append(current_rule_data)
            # Create new rule button with consistent styling
            new_rule_button = html.Button(
                f"Rule {len(rules)}", 
                id={'type': 'rule-button', 'index': current_rule_data['id']},
                style={'margin': '5px', 'padding': '5px 10px'}
            )
            
            # Initialize or append to rule list
            rule_list_children = (rule_list_children or []) + [new_rule_button]
            return rules, rule_list_children
        
        return dash.no_update, dash.no_update

    @app.callback(
        [Output('current-rule', 'data', allow_duplicate=True),
        Output('rule-creation-area', 'style', allow_duplicate=True)],
        Input({'type': 'rule-button', 'index': ALL}, 'n_clicks'),
        State('rules-store', 'data'),
        prevent_initial_call=True
    )
    def load_rule(n_clicks, rules):
        print("load_rule callback triggered")
        ctx = dash.callback_context
        if not ctx.triggered or not any(n_clicks):
            return dash.no_update, dash.no_update

        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        rule_id = button_id['index']

        # Find the clicked button's index in the n_clicks_list
        triggered_value = ctx.triggered[0]['value']

        if triggered_value is not None and triggered_value > 0:
            print(rules)
            for rule in rules:
                if rule['id'] == rule_id:
                    rule['id'] = str(uuid.uuid4())
                    return rule, {'display': 'block'}

        return dash.no_update, dash.no_update

    @app.callback(
        Output('main-graph', 'elements', allow_duplicate=True),
        Input('apply-rule-button', 'n_clicks'),
        State('main-graph', 'elements'),
        State('main-graph', 'selectedNodeData'),
        State('main-graph', 'selectedEdgeData'),
        State('rules-store', 'data'),
        prevent_initial_call=True
    )
    def apply_rule(n_clicks, elements, selected_nodes, selected_edges, rules):
        print("apply_rule callback triggered")
        if n_clicks > 0 and rules:
            # For simplicity, we'll apply the last created rule
            rule = rules[-1]
            
            # Check if the selected subgraph matches the LHS
            if match_subgraph(selected_nodes, selected_edges, rule['lhs']):
                # Remove elements not in K
                elements = [e for e in elements if e['data']['id'] in rule['k']['nodes'] or 
                            (e['data'].get('source') and f"{e['data']['source']}-{e['data']['target']}" in rule['k']['edges'])]
                
                # Add elements from RHS
                for element in rule['rhs']:
                    if element not in elements:
                        elements.append(element)
        
        return elements

    @app.callback(
        Output('current-rule', 'data', allow_duplicate=True),
        Input('create-new-rule-button', 'n_clicks'),
        [State('main-graph', 'selectedNodeData'),
        State('main-graph', 'selectedEdgeData'),
        State('current-rule', 'data')],
        prevent_initial_call=True
    )
    def initialize_new_rule(n_clicks, selected_nodes, selected_edges, current_rule_data):
        print("initialize_new_rule callback triggered")
        if n_clicks > 0:
            current_rule = RuleManager.initialize_from_selection(selected_nodes, selected_edges)
            return current_rule.to_dict()
        return dash.no_update

    @app.callback(
        Output('current-rule', 'data', allow_duplicate=True),
        Input('select-k-button', 'n_clicks'),
        [State('lhs-graph', 'selectedNodeData'),
        State('lhs-graph', 'selectedEdgeData'),
        State('current-rule', 'data')],
        prevent_initial_call=True
    )
    def select_k(n_clicks, selected_nodes, selected_edges, current_rule_data):
        print("select_k callback triggered")
        if n_clicks > 0:
            current_rule = RuleManager.from_dict(current_rule_data)
            current_rule.update_k_elements(selected_nodes, selected_edges)
            return current_rule.to_dict()
        return dash.no_update
    
    