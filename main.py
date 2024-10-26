import dash
from dash import html, dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State
import networkx as nx
import json

app = dash.Dash(__name__)
G = nx.Graph()
G_rhs = nx.Graph()

app.layout = html.Div([
    cyto.Cytoscape(
        id='main-graph',
        elements=[],
        style={'width': '100%', 'height': '400px'},
        layout={'name': 'breadthfirst'},
    ),
    html.Div([
        html.Button('Add Node', id='add-node-button', n_clicks=0),
        html.Button('Add Edge', id='add-edge-button', n_clicks=0),
        html.Button('Remove Selected', id='remove-selected-button', n_clicks=0),
    ], style={'textAlign': 'center', 'marginTop': '10px', 'marginBottom': '10px'}),
    html.Div([
        html.Button('Create Rule', id='create-rule-button', n_clicks=0),
        html.Button('Apply Rule', id='apply-rule-button', n_clicks=0),
    ], style={'textAlign': 'center', 'marginTop': '10px', 'marginBottom': '10px'}),
    html.Div(id='click-data'),
    html.Div(id='selected-data'),
    html.Div(id='rule-creation-area', children=[
        html.Div([
            html.Div([
                cyto.Cytoscape(
                    id='lhs-graph',
                    elements=[],
                    style={'width': '100%', 'height': '300px'},
                    layout={'name': 'breadthfirst'},
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(id)'
                            }
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'curve-style': 'bezier'
                            }
                        },
                        {
                            'selector': '.k-element',
                            'style': {
                                'background-color': '#FF0000',
                                'line-color': '#FF0000'
                            }
                        },
                        {
                            'selector': '.k-element:selected',
                            'style': {
                                'background-color': '#8B0000',  # Dark red
                                'line-color': '#8B0000'  # Dark red
                            }
                        }
                    ]
                ),
                html.Div([
                    html.Button('Add Node (LHS)', id='add-lhs-node-button', n_clicks=0),
                    html.Button('Add Edge (LHS)', id='add-lhs-edge-button', n_clicks=0),
                    html.Button('Remove Selected (LHS)', id='remove-lhs-selected-button', n_clicks=0),
                ], style={'textAlign': 'center', 'marginTop': '10px'}),
                html.Div([
                    html.Button('Select K', id='select-k-button', n_clicks=0),
                    html.Button('Finalize Rule', id='finalize-rule-button', n_clicks=0),
                ], style={'textAlign': 'center', 'marginTop': '10px'}),
            ], style={'width': '45%', 'float': 'left'}),
            html.Div([
                cyto.Cytoscape(
                    id='rhs-graph',
                    elements=[],
                    style={'width': '100%', 'height': '300px'},
                    layout={'name': 'breadthfirst'},
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(id)'
                            }
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'curve-style': 'bezier'
                            }
                        },
                        {
                            'selector': '.k-element',
                            'style': {
                                'background-color': '#FF0000',
                                'line-color': '#FF0000'
                            }
                        },
                        {
                            'selector': '.k-element:selected',
                            'style': {
                                'background-color': '#8B0000',  # Dark red
                                'line-color': '#8B0000'  # Dark red
                            }
                        }
                    ]
                ),
                html.Div([
                    html.Button('Add Node (RHS)', id='add-rhs-node-button', n_clicks=0),  
                    html.Button('Add Edge (RHS)', id='add-rhs-edge-button', n_clicks=0),  
                    html.Button('Remove Selected (RHS)', id='remove-rhs-selected-button', n_clicks=0),
                ], style={'textAlign': 'center', 'marginTop': '10px'}),
            ], style={'width': '45%', 'float': 'right'}),
        ]),
    ], style={'display': 'none'}),
    dcc.Store(id='current-rule', data={}),
    html.Div(id='rule-list'),
    dcc.Store(id='rules-store', data=[]),
])

# main graph

@app.callback(
    Output('main-graph', 'elements'),
    [Input('add-node-button', 'n_clicks'),
     Input('add-edge-button', 'n_clicks'),
     Input('apply-rule-button', 'n_clicks'),
     Input('remove-selected-button', 'n_clicks')],  # New input
    [State('main-graph', 'elements'),
     State('main-graph', 'selectedNodeData'),
     State('main-graph', 'selectedEdgeData')]  # Added selectedEdgeData
)
def update_graph(n_clicks_node, n_clicks_edge, n_clicks_rule, n_clicks_remove, elements, selected_nodes, selected_edges):
    global G
    ctx = dash.callback_context
    if not ctx.triggered:
        return elements
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'add-node-button':
            node_id = str(len(elements) + 1)
            elements.append({'data': {'id': node_id, 'label': node_id}})
            G.add_node(node_id)
        elif button_id == 'add-edge-button':
            if selected_nodes:
                selected_ids = [node['id'] for node in selected_nodes]
                if len(selected_ids) >= 2:
                    for i in range(len(selected_ids)):
                        for j in range(i + 1, len(selected_ids)):
                            source, target = selected_ids[i], selected_ids[j]
                            edge_id = f"{source}-{target}"
                            if not G.has_edge(source, target):
                                elements.append({'data': {'id': edge_id, 'source': source, 'target': target}})
                                G.add_edge(source, target)
        elif button_id == 'apply-rule-button':
            # Implement DPO rewriting logic
            pass  # Placeholder for rule application
        elif button_id == 'remove-selected-button':
            elements, G = remove_selected_elements(elements, selected_nodes, selected_edges, G)
    return elements

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

# secondary graphs

@app.callback(
    Output('rule-creation-area', 'style'),
    Input('create-rule-button', 'n_clicks'),
)
def show_rule_creation_area(n_clicks):
    if n_clicks > 0:
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    [Output('lhs-graph', 'elements'),
     Output('rhs-graph', 'elements')],
    Input('create-rule-button', 'n_clicks'),
    State('main-graph', 'selectedNodeData'),
    State('main-graph', 'selectedEdgeData')
)
def initialize_rule_graphs(n_clicks, selected_nodes, selected_edges):
    global G_rhs
    if n_clicks > 0:
        elements = []
        selected_node_ids = set()
        if selected_nodes:
            for node in selected_nodes:
                elements.append({'data': {'id': node['id'], 'label': node['label']}})
                selected_node_ids.add(node['id'])
        if selected_edges:
            for edge in selected_edges:
                if edge['source'] in selected_node_ids and edge['target'] in selected_node_ids:
                    elements.append({'data': {'source': edge['source'], 'target': edge['target']}})
        
        # Initialize the RHS graph
        G_rhs = nx.Graph()
        for element in elements:
            if 'id' in element['data']:
                G_rhs.add_node(element['data']['id'])
            elif 'source' in element['data']:
                G_rhs.add_edge(element['data']['source'], element['data']['target'])
        
        return elements, elements
    return [], []

@app.callback(
    Output('current-rule', 'data'),
    Input('select-k-button', 'n_clicks'),
    State('lhs-graph', 'selectedNodeData'),
    State('lhs-graph', 'selectedEdgeData'),
    State('current-rule', 'data')
)
def select_k(n_clicks, selected_nodes, selected_edges, current_rule):
    if n_clicks > 0:
        k_nodes = set(node['id'] for node in selected_nodes) if selected_nodes else set()
        k_edges = []
        
        # Only include edges where both nodes are in k_nodes
        if selected_edges:
            for edge in selected_edges:
                if edge['source'] in k_nodes and edge['target'] in k_nodes:
                    k_edges.append(f"{edge['source']}-{edge['target']}")
        
        current_rule['k'] = {
            'nodes': list(k_nodes),
            'edges': k_edges
        }
    return current_rule

@app.callback(
    [Output('lhs-graph', 'elements', allow_duplicate=True),
     Output('rhs-graph', 'elements', allow_duplicate=True)],
    [Input('current-rule', 'data'),
     Input('remove-lhs-selected-button', 'n_clicks'),
     Input('add-lhs-node-button', 'n_clicks'),
     Input('add-lhs-edge-button', 'n_clicks')],
    [State('lhs-graph', 'elements'),
     State('rhs-graph', 'elements'),
     State('lhs-graph', 'selectedNodeData'),
     State('lhs-graph', 'selectedEdgeData')],
    prevent_initial_call=True
)
def update_lhs_graph(current_rule, n_clicks_remove, n_clicks_add_node, n_clicks_add_edge, 
                     lhs_elements, rhs_elements, lhs_selected_nodes, lhs_selected_edges):
    global G, G_rhs
    ctx = dash.callback_context
    if not ctx.triggered:
        return lhs_elements, rhs_elements
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'current-rule':
        k_nodes = set(current_rule.get('k', {}).get('nodes', []))
        k_edges = set(current_rule.get('k', {}).get('edges', []))
        
        for element in lhs_elements:
            if 'id' in element['data']:
                if element['data']['id'] in k_nodes or \
                (element['data'].get('source') and f"{element['data']['source']}-{element['data']['target']}" in k_edges):
                    element['classes'] = 'k-element'
                else:
                    element['classes'] = ''
    elif trigger_id == 'remove-lhs-selected-button':
        lhs_elements, _ = remove_selected_elements(lhs_elements, lhs_selected_nodes, lhs_selected_edges)
    elif trigger_id == 'add-lhs-node-button':
        node_id = f"lhs_{len(lhs_elements) + 1}"
        new_node = {'data': {'id': node_id, 'label': node_id}}
        lhs_elements.append(new_node)
        rhs_elements.append(new_node)  # Add the new node to RHS as well
        G_rhs.add_node(node_id)
    elif trigger_id == 'add-lhs-edge-button':
        if lhs_selected_nodes:
            selected_ids = [node['id'] for node in lhs_selected_nodes]
            if len(selected_ids) >= 2:
                for i in range(len(selected_ids)):
                    for j in range(i + 1, len(selected_ids)):
                        source, target = selected_ids[i], selected_ids[j]
                        edge_id = f"{source}-{target}"
                        if not any(e['data'].get('source') == source and e['data'].get('target') == target for e in lhs_elements):
                            new_edge = {'data': {'id': edge_id, 'source': source, 'target': target}}
                            lhs_elements.append(new_edge)
                            rhs_elements.append(new_edge)  # Add the new edge to RHS as well
                            G_rhs.add_edge(source, target)
        
    return lhs_elements, rhs_elements

@app.callback(
    Output('rhs-graph', 'elements', allow_duplicate=True),
    [Input('current-rule', 'data'),
     Input('remove-rhs-selected-button', 'n_clicks'),
     Input('add-rhs-node-button', 'n_clicks'),
     Input('add-rhs-edge-button', 'n_clicks')],
    [State('rhs-graph', 'elements'),
     State('rhs-graph', 'selectedNodeData'),
     State('rhs-graph', 'selectedEdgeData')],
    prevent_initial_call=True
)
def update_rhs_graph(current_rule, n_clicks_remove, n_clicks_add_node, n_clicks_add_edge, 
                     elements, rhs_selected_nodes, rhs_selected_edges):

    global G_rhs
    ctx = dash.callback_context
    if not ctx.triggered:
        return elements
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'current-rule':
        k_nodes = set(current_rule.get('k', {}).get('nodes', []))
        k_edges = set(current_rule.get('k', {}).get('edges', []))
        
        for element in elements:
            if 'id' in element['data']:
                if element['data']['id'] in k_nodes or \
                (element['data'].get('source') and f"{element['data']['source']}-{element['data']['target']}" in k_edges):
                    element['classes'] = 'k-element'
                else:
                    element['classes'] = ''
    elif trigger_id == 'remove-rhs-selected-button':
        k_nodes = set(current_rule.get('k', {}).get('nodes', []))
        k_edges = set(current_rule.get('k', {}).get('edges', []))
        
        # Filter out selected nodes and edges that are not in K
        if rhs_selected_nodes:
            rhs_selected_nodes = [node for node in rhs_selected_nodes if node['id'] not in k_nodes]
        if rhs_selected_edges:
            rhs_selected_edges = [edge for edge in rhs_selected_edges if f"{edge['source']}-{edge['target']}" not in k_edges]

        elements, G_rhs = remove_selected_elements(elements, rhs_selected_nodes, rhs_selected_edges, G_rhs)
    elif trigger_id == 'add-rhs-node-button':
        node_id = f"rhs_{len(elements) + 1}"
        elements.append({'data': {'id': node_id, 'label': node_id}})
        G_rhs.add_node(node_id)
    elif trigger_id == 'add-rhs-edge-button':
        if rhs_selected_nodes:
            selected_ids = [node['id'] for node in rhs_selected_nodes]
            if len(selected_ids) >= 2:
                for i in range(len(selected_ids)):
                    for j in range(i + 1, len(selected_ids)):
                        source, target = selected_ids[i], selected_ids[j]
                        edge_id = f"{source}-{target}"
                        if not G_rhs.has_edge(source, target):
                            elements.append({'data': {'id': edge_id, 'source': source, 'target': target}})
                            G_rhs.add_edge(source, target)
        
    return elements

@app.callback(
    [Output('rules-store', 'data'),
     Output('rule-list', 'children')],
    Input('finalize-rule-button', 'n_clicks'),
    State('lhs-graph', 'elements'),
    State('rhs-graph', 'elements'),
    State('current-rule', 'data'),
    State('rules-store', 'data')
)
def finalize_rule(n_clicks, lhs_elements, rhs_elements, current_rule, rules):
    global G_rhs
    if n_clicks > 0:
        new_rule = {
            'lhs': lhs_elements,
            'k': current_rule.get('k', {'nodes': [], 'edges': []}),
            'rhs': rhs_elements,
            'rhs_graph': nx.node_link_data(G_rhs)  # Store the NetworkX graph as node-link data
        }
        rules.append(new_rule)
        # Reset the RHS graph for the next rule
        G_rhs = nx.Graph()
        return rules, [html.Div(f"Rule {i+1}") for i in range(len(rules))]
    return rules, [html.Div(f"Rule {i+1}") for i in range(len(rules))]



def remove_selected_elements(elements, selected_nodes, selected_edges, graph=None):
    if not selected_nodes and not selected_edges:
        return elements, graph

    selected_node_ids = set(node['id'] for node in selected_nodes) if selected_nodes else set()
    
    # Remove selected nodes and their connected edges from the graph
    if graph is not None:
        graph.remove_nodes_from(selected_node_ids)
    
    # Filter out selected nodes and their connected edges from elements
    new_elements = [
        e for e in elements
        if ('id' in e['data'] and e['data']['id'] not in selected_node_ids) and
           ('source' not in e['data'] or (e['data']['source'] not in selected_node_ids and e['data']['target'] not in selected_node_ids))
    ]
    
    # Remove selected edges only if both connected nodes are not selected
    if selected_edges:
        selected_edge_ids = set(f"{edge['source']}-{edge['target']}" for edge in selected_edges)
        new_elements = [
            e for e in new_elements
            if 'source' not in e['data'] or f"{e['data']['source']}-{e['data']['target']}" not in selected_edge_ids
        ]
        
        # Remove selected edges from the graph
        if graph is not None:
            for edge in selected_edges:
                if edge['source'] in graph.nodes() and edge['target'] in graph.nodes():
                    graph.remove_edge(edge['source'], edge['target'])
    
    return new_elements, graph

def match_subgraph(selected_nodes, selected_edges, lhs):
    # This is a simplified matching function
    # You may need to implement a more sophisticated matching algorithm
    if selected_nodes:
        selected_node_ids = set(node['id'] for node in selected_nodes)
    else:
        selected_node_ids = set()
    if selected_edges:
        selected_edge_ids = set(f"{edge['source']}-{edge['target']}" for edge in selected_edges)
    else:
        selected_edge_ids = set()
    
    lhs_node_ids = set(node['data']['id'] for node in lhs if 'id' in node['data'])
    lhs_edge_ids = set(f"{edge['data']['source']}-{edge['data']['target']}" for edge in lhs if 'source' in edge['data'])
    
    return selected_node_ids == lhs_node_ids and selected_edge_ids == lhs_edge_ids


if __name__ == '__main__':
    app.run_server(debug=True)
