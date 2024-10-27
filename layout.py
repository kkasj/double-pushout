import dash
from dash import html, dcc
import dash_cytoscape as cyto

from utils import get_default_graph_layout

def create_layout():
    blue = '#87CEEB'

    # Define common button styles
    button_style = {
        'margin': '5px',
        'padding': '8px 16px',
        'backgroundColor': blue,
        'color': 'white',
        'border': 'none',
        'borderRadius': '4px',
        'cursor': 'pointer',
        'fontSize': '14px',
        'transition': 'background-color 0.3s'
    }

    # Define container styles
    container_style = {
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif'
    }

    graph_container_style = {
        'border': '1px solid #ddd',
        'borderRadius': '8px',
        'padding': '15px',
        'marginBottom': '20px',
        'backgroundColor': '#f9f9f9'
    }


    # New predefined styles
    rule_creation_container_style = {
        'overflow': 'hidden',  # This ensures floating children are contained
        'backgroundColor': '#ffffff',
        'border': '1px solid #e1e1e1',
        'borderRadius': '10px',
        'padding': '20px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
        'marginTop': '20px',
        'display': 'flex',  # Use flexbox instead of float
        'justifyContent': 'space-between',  # Distribute space between items
        'gap': '20px'  # Add space between the two sides
    }

    graph_side_container_style = {
        'width': '48%',  # Slightly less than 50% to account for padding and gap
        'minWidth': '400px',  # Prevent containers from getting too narrow
    }

    graph_panel_style = {
        'border': '1px solid #ddd',
        'borderRadius': '8px',
        'padding': '15px',
        'backgroundColor': '#f9f9f9',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'marginBottom': '15px'  # Add space between graph and buttons
    }

    heading_style = {
        'color': '#34495E',
        'textAlign': 'center',
        'marginBottom': '15px'
    }

    button_container_style = {
        'textAlign': 'center',
        'marginTop': '15px'
    }




    return html.Div([
        # Header
        html.H1('Graph DPO Transformation Tool', 
                style={'textAlign': 'center', 'color': '#2C3E50', 'marginBottom': '30px'}),
        
        # Main container
        html.Div([
            # Main graph section
            html.Div([
                html.H2('Host Graph', style={'color': '#34495E', 'marginBottom': '15px'}),
                cyto.Cytoscape(
                    id='main-graph',
                    elements=[],
                    style={'width': '100%', 'height': '400px', 'backgroundColor': 'white'},
                    layout=get_default_graph_layout(),
                )
            ], style=graph_container_style),

            # Main graph controls
            html.Div([
                html.Button('Add Node', id='add-node-button', n_clicks=0, style=button_style),
                html.Button('Add Edge', id='add-edge-button', n_clicks=0, style=button_style),
                html.Button('Remove Selected', id='remove-selected-button', n_clicks=0, 
                           style={**button_style, 'backgroundColor': '#E74C3C'}),
                html.Button('Reset View', id='reset-view-button', n_clicks=0, style=button_style),
            ], style={'textAlign': 'center', 'marginBottom': '20px'}),


            # Rule list section
            html.Div([
                html.H3('Available Rules', style={'color': '#34495E', 'marginBottom': '10px'}),
                html.Div(id='rule-list', style={
                    'border': '1px solid #ddd',
                    'borderRadius': '4px',
                    'padding': '10px',
                    'minHeight': '50px'
                }),
            ], style={'marginBottom': '20px'}),

            # Rule creation area
            html.Div(id='rule-creation-area', children=[
                # Rule controls
                html.Div([
                    html.Button('Create New Rule', id='create-new-rule-button', n_clicks=0, 
                            style={**button_style, 'backgroundColor': blue}),
                    html.Button('Finalize Rule', id='finalize-rule-button', n_clicks=0, 
                            style={**button_style, 'backgroundColor': blue}),
                    html.Button('Apply Rules', id='apply-rules-button', n_clicks=0, 
                            style={**button_style, 'backgroundColor': blue}),
                ], style={'textAlign': 'center', 'marginBottom': '20px'}),

                html.Div([
                    # LHS Graph
                    html.Div([
                        html.H3('L', style=heading_style),
                        html.Div([
                            cyto.Cytoscape(
                                id='lhs-graph',
                                elements=[],
                                style={'width': '100%', 'height': '300px', 'backgroundColor': 'white'},
                                layout=get_default_graph_layout(),
                                stylesheet=[
                                    {
                                        'selector': 'node',
                                        'style': {
                                            'content': 'data(id)',
                                            'font-size': '12px'
                                        }
                                    },
                                    {
                                        'selector': 'edge',
                                        'style': {
                                            'curve-style': 'bezier',
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
                        ], style=graph_panel_style),
                        html.Div([
                            html.Button('Add Node', id='add-lhs-node-button', n_clicks=0, style=button_style),
                            html.Button('Add Edge', id='add-lhs-edge-button', n_clicks=0, style=button_style),
                            html.Button('Remove Selected', id='remove-lhs-selected-button', n_clicks=0, 
                                    style={**button_style, 'backgroundColor': '#E74C3C'}),
                            html.Button('Reset View', id='reset-lhs-view-button', n_clicks=0, style=button_style),
                            html.Button('Select K', id='select-k-button', n_clicks=0, 
                                    style={**button_style, 'backgroundColor': '#F39C12'}),
                        ], style=button_container_style),
                    ], style=graph_side_container_style),

                    # RHS Graph
                    html.Div([
                        html.H3('R', style=heading_style),
                        html.Div([
                            cyto.Cytoscape(
                                id='rhs-graph',
                                elements=[],
                                style={'width': '100%', 'height': '300px', 'backgroundColor': 'white'},
                                layout=get_default_graph_layout(),
                                stylesheet=[
                                    {
                                        'selector': 'node',
                                        'style': {
                                            'content': 'data(id)',
                                            'font-size': '12px'
                                        }
                                    },
                                    {
                                        'selector': 'edge',
                                        'style': {
                                            'curve-style': 'bezier',
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
                        ], style=graph_panel_style),
                        html.Div([
                            html.Button('Add Node', id='add-rhs-node-button', n_clicks=0, style=button_style),
                            html.Button('Add Edge', id='add-rhs-edge-button', n_clicks=0, style=button_style),
                            html.Button('Remove Selected', id='remove-rhs-selected-button', n_clicks=0, 
                                    style={**button_style, 'backgroundColor': '#E74C3C'}),
                            html.Button('Reset View', id='reset-rhs-view-button', n_clicks=0, style=button_style),
                            html.Button('Reset to LHS', id='reset-rhs-to-lhs-button', n_clicks=0, 
                                    style={**button_style, 'backgroundColor': '#808080'}),
                        ], style=button_container_style),
                    ], style=graph_side_container_style),
                ], style=rule_creation_container_style),
            ], style={'display': 'block', 'marginTop': '20px'}),

            # Storage
            dcc.Store(id='current-rule', data={}),
            dcc.Store(id='rules-store', data=[]),
        ], style=container_style)
    ])