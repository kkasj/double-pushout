import dash
from dash import html, dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State, ALL
from copy import deepcopy
import networkx as nx
import json
import uuid

from classes import GraphManager, RuleManager
from dpo import match_subgraph, apply_dpo_rule, apply_rule_parallel
from utils.file_operations import save_rule_to_file, load_rules_from_directory, load_saved_rules_list, delete_rule_file

def register_rule_callbacks(app):
    @app.callback(
        [Output('rules-store', 'data', allow_duplicate=True),
        Output('rule-list', 'children', allow_duplicate=True),
        Output('current-rule', 'data', allow_duplicate=True)],
        Input('finalize-rule-button', 'n_clicks'),
        [State('rules-store', 'data'),
        State('current-rule', 'data'),
        State('rule-list', 'children')],
        prevent_initial_call=True
    )
    def finalize_rule(n_clicks, rules, current_rule_data, rule_list_children):
        print("finalize_rule callback triggered")
        if n_clicks > 0:
            current_rule_data_copy = deepcopy(current_rule_data)
            rules.append(current_rule_data_copy)
            
            # Create container div for rule buttons
            rule_container = html.Div([
                html.Button(
                    f"Rule {len(rules)}", 
                    id={'type': 'rule-button', 'index': current_rule_data_copy['id']},
                    style={'margin': '5px', 'padding': '5px 10px'}
                ),
                html.Button(
                    "✕",
                    id={'type': 'remove-rule-button', 'index': current_rule_data_copy['id']},
                    style={
                        'margin': '5px',
                        'padding': '5px 10px',
                        'backgroundColor': '#ff4444',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '3px'
                    }
                )
            ], style={'display': 'inline-block'})
            
            rule_list_children = (rule_list_children or []) + [rule_container]
            current_rule_data['id'] = str(uuid.uuid4())
            return rules, rule_list_children, current_rule_data
        
        return dash.no_update, dash.no_update, dash.no_update

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
        [Output('main-graph', 'elements', allow_duplicate=True),
         Output('alert-store', 'data', allow_duplicate=True)],
        Input('apply-rules-button', 'n_clicks'),
        [State('main-graph', 'elements'),
         State('rules-store', 'data')],
        prevent_initial_call=True
    )
    def apply_rules(n_clicks, elements, rules):
        print("apply_rules callback triggered")
        if n_clicks > 0:
            if not rules:
                return dash.no_update, "No rules available to apply. Please create and save at least one rule first."
            
            total_applications = 0
            for rule in rules:
                rule_manager = RuleManager.from_dict(rule)
                host_graph_manager = GraphManager.from_elements(elements)

                print("Host graph nodes:")
                print(host_graph_manager.graph.nodes())
                print(host_graph_manager.graph.edges())

                # Find all matches of LHS in the host graph
                successful_applications = apply_rule_parallel(host_graph_manager, rule_manager)
                total_applications += successful_applications

                print("Host graph nodes after rule application:")
                print(host_graph_manager.graph.nodes())
                print(host_graph_manager.graph.edges())

                if successful_applications > 0:
                    print(f"Rule applied successfully {successful_applications} times")
                    elements = host_graph_manager.elements
                else:
                    print(f"No applicable match found for rule {rule_manager.id}")

            # Return appropriate alert message based on total applications
            if total_applications > 0:
                return elements, {'message': f"Rules applied successfully! Total transformations: {total_applications}", 'type': 'success'}
            else:
                return dash.no_update, {'message': "No rules could be applied to the current graph. Check if your rules match any part of the graph.", 'type': 'error'}
        
        return dash.no_update, dash.no_update

    @app.callback(
        Output('current-rule', 'data', allow_duplicate=True),
        Input('create-new-rule-button', 'n_clicks'),
        [State('main-graph', 'selectedNodeData'),
        State('main-graph', 'selectedEdgeData')],
        prevent_initial_call=True
    )
    def initialize_new_rule(n_clicks, selected_nodes, selected_edges):
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
            print("Current rule LHS nodes:")
            print(current_rule.lhs.graph.nodes())
            print(current_rule.lhs.graph.edges())
            print("Current rule RHS nodes:")
            print(current_rule.rhs.graph.nodes())
            print(current_rule.rhs.graph.edges())
            print("Selected nodes:")
            print(selected_nodes)
            print("Selected edges:")
            print(selected_edges)
            current_rule.update_k_elements(selected_nodes, selected_edges)
            return current_rule.to_dict()
        return dash.no_update
    

    @app.callback(
        [Output('rules-store', 'data', allow_duplicate=True),
        Output('rule-list', 'children', allow_duplicate=True)],
        Input({'type': 'remove-rule-button', 'index': ALL}, 'n_clicks'),
        [State('rules-store', 'data'),
        State('rule-list', 'children')],
        prevent_initial_call=True
    )
    def remove_rule(n_clicks_list, rules, rule_list_children):
        ctx = dash.callback_context
        if not ctx.triggered or not any(n_clicks_list):
            return dash.no_update, dash.no_update

        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        rule_id = button_id['index']

        # Remove rule from rules store
        updated_rules = [rule for rule in rules if rule['id'] != rule_id]
        
        # Remove rule from rule list
        updated_rule_list = [
            child for child in rule_list_children 
            if not (isinstance(child, dict) and 
                   child.get('props', {}).get('children', []) and 
                   any(btn.get('props', {}).get('id', {}).get('index') == rule_id 
                       for btn in child['props']['children']))
        ]

        return updated_rules, updated_rule_list
    
    @app.callback(
        Output('alert-container', 'children', allow_duplicate=True),
        Input('alert-store', 'data'),
        prevent_initial_call=True
    )
    def display_alert(alert_data):
        if not alert_data:
            return None
        
        # Handle both string and dict formats for backward compatibility
        if isinstance(alert_data, str):
            message = alert_data
            alert_type = 'error'
        else:
            message = alert_data.get('message', '')
            alert_type = alert_data.get('type', 'error')
        
        # Define styles based on alert type
        base_style = {
            'padding': '15px',
            'borderRadius': '4px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.2)',
            'marginBottom': '10px',
            'textAlign': 'center'
        }
        
        if alert_type == 'success':
            style = {
                **base_style,
                'backgroundColor': '#4CAF50',  # Green background
                'color': 'white',
            }
        else:  # error
            style = {
                **base_style,
                'backgroundColor': '#f44336',  # Red background
                'color': 'white',
            }
        
        return html.Div(message, style=style)

    @app.callback(
        [Output('alert-store', 'data', allow_duplicate=True),
         Output('saved-rules-list', 'children', allow_duplicate=True)],
        Input('save-rule-button', 'n_clicks'),
        [State('current-rule', 'data')],
        prevent_initial_call=True
    )
    def save_current_rule(n_clicks, current_rule_data):
        if n_clicks > 0:
            try:
                save_rule_to_file(current_rule_data)
                return "Rule saved to file successfully!", load_saved_rules_list()
            except Exception as e:
                return f"Error saving rule: {str(e)}", dash.no_update
        return dash.no_update, dash.no_update

    @app.callback(
        [Output('alert-store', 'data', allow_duplicate=True),
         Output('saved-rules-list', 'children', allow_duplicate=True)],
        Input({'type': 'delete-saved-rule-button', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def delete_saved_rule(n_clicks_list):
        ctx = dash.callback_context
        if not ctx.triggered or not any(n_clicks_list):
            return dash.no_update, dash.no_update

        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        rule_id = button_id['index']
        
        try:
            if delete_rule_file(rule_id):
                return "Rule deleted successfully!", load_saved_rules_list()
            else:
                return "Error: Rule file not found", dash.no_update
        except Exception as e:
            return f"Error deleting rule: {str(e)}", dash.no_update
    
    @app.callback(
        Output('saved-rules-list', 'children'),
        Input('_refresh', 'children'),
        prevent_initial_call=False 
    )
    def on_page_refresh(refresh_timestamp):
        return load_saved_rules_list()

    @app.callback(
        [Output('current-rule', 'data', allow_duplicate=True),
         Output('rule-creation-area', 'style', allow_duplicate=True)],
        Input({'type': 'load-saved-rule-button', 'index': ALL}, 'n_clicks'),
        State('rules-store', 'data'),
        prevent_initial_call=True
    )
    def load_saved_rule(n_clicks_list, rules):
        ctx = dash.callback_context
        if not ctx.triggered or not any(n_clicks_list):
            return dash.no_update, dash.no_update

        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        rule_id = button_id['index']

        # Load rules from directory
        saved_rules = load_rules_from_directory()
        
        # Find the rule with matching ID
        for rule in saved_rules:
            if rule['id'] == rule_id:
                # Generate new ID for the loaded rule
                rule['id'] = str(uuid.uuid4())
                return rule, {'display': 'block'}

        return dash.no_update, dash.no_update
