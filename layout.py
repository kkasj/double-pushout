import dash
from dash import html, dcc
import dash_cytoscape as cyto

def create_layout():
    return html.Div([
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
            html.Button('Create New Rule', id='create-new-rule-button', n_clicks=0),
            html.Button('Finalize Rule', id='finalize-rule-button', n_clicks=0),
            html.Button('Apply Rule', id='apply-rule-button', n_clicks=0),
        ], style={'textAlign': 'center', 'marginTop': '10px', 'marginBottom': '10px'}),
        html.Div(id='click-data'),
        html.Div(id='selected-data'),
        html.Div([
            html.Div(id='rule-list'),
        ], style={'textAlign': 'center', 'marginTop': '10px', 'marginBottom': '10px'}),
        html.Div(id='rule-creation-area', children=[
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
                                'background-color': '#FF0000',  # red
                                'line-color': '#FF0000'  # red
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
        ], style={'display': 'block'}),
        dcc.Store(id='current-rule', data={}),
        dcc.Store(id='rules-store', data=[]),
    ])