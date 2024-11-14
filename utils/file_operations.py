import os
import json
from datetime import datetime
import dash
from dash import html

def save_rule_to_file(rule_data, rules_dir="saved_rules"):
    """
    Save a rule to a JSON file in the specified directory.
    
    Parameters
    ----------
    rule_data : dict
        The rule data to save
    rules_dir : str, optional
        Directory where rules should be saved
    
    Returns
    -------
    str
        Path to the saved file
    """
    # Create directory if it doesn't exist
    if not os.path.exists(rules_dir):
        os.makedirs(rules_dir)
    
    # Get current highest index
    current_index = 0
    for filename in os.listdir(rules_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(rules_dir, filename), 'r') as f:
                    file_data = json.load(f)
                    if 'index' in file_data and file_data['index'] > current_index:
                        current_index = file_data['index']
            except:
                continue
    
    # Add index to rule data
    rule_data['index'] = current_index + 1
    
    # Generate filename using timestamp and rule ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rule_{timestamp}_{rule_data['id'][:8]}.json"
    filepath = os.path.join(rules_dir, filename)
    
    # Save rule to file
    with open(filepath, 'w') as f:
        json.dump(rule_data, f, indent=2)
    
    return filepath

def load_rules_from_directory(rules_dir="saved_rules"):
    """
    Load all rules from the specified directory.
    
    Parameters
    ----------
    rules_dir : str, optional
        Directory containing saved rules
    
    Returns
    -------
    list
        List of rule data dictionaries
    """
    rules = []
    
    if not os.path.exists(rules_dir):
        return rules
        
    for filename in os.listdir(rules_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(rules_dir, filename)
            with open(filepath, 'r') as f:
                rule_data = json.load(f)
                rules.append(rule_data)
    
    return rules
    
def load_saved_rules_list():
    """Load the list of saved rules from the directory."""
    rules = load_rules_from_directory()
    print(rules)
    rule_buttons = []
    for rule in rules:
        rule_index = rule.get('index', '?')
        rule_container = html.Div([
            html.Button(
                f"Load Rule {rule_index}",
                id={'type': 'load-saved-rule-button', 'index': rule['id']},
                style={
                    'margin': '5px',
                    'padding': '5px 10px',
                    'backgroundColor': '#3498DB',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer'
                }
            ),
            html.Button(
                "✕",
                id={'type': 'delete-saved-rule-button', 'index': rule['id']},
                style={
                    'margin': '5px',
                    'padding': '5px 10px',
                    'backgroundColor': '#ff4444',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '3px',
                    'cursor': 'pointer'
                }
            )
        ], style={'display': 'block'})
        rule_buttons.append(rule_container)
    return rule_buttons

def save_graph_to_file(graph_data, graphs_dir="saved_graphs"):
    """
    Save a graph to a JSON file in the specified directory.
    
    Parameters
    ----------
    graph_data : dict
        The graph data to save
    graphs_dir : str, optional
        Directory where graphs should be saved
    
    Returns
    -------
    str
        Path to the saved file
    """
    # Create directory if it doesn't exist
    if not os.path.exists(graphs_dir):
        os.makedirs(graphs_dir)
    
    # Generate filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"graph_{timestamp}.json"
    filepath = os.path.join(graphs_dir, filename)
    
    # Save graph to file
    with open(filepath, 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    return filepath

def load_graph_from_file(filepath):
    """
    Load a graph from a JSON file.
    
    Parameters
    ----------
    filepath : str
        Path to the JSON file
    
    Returns
    -------
    dict
        The loaded graph data
    """
    with open(filepath, 'r') as f:
        graph_data = json.load(f)
    return graph_data

def delete_rule_file(rule_id, rules_dir="saved_rules"):
    """Delete a rule file based on the rule ID."""
    if not os.path.exists(rules_dir):
        return False
        
    target_file = None
    # First find the file without opening it
    for filename in os.listdir(rules_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(rules_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    rule_data = json.load(f)
                    if rule_data['id'] == rule_id:
                        target_file = filepath
                        break
            except Exception:
                continue

    # If we found the file, try to delete it
    if target_file:
        try:
            os.remove(target_file)
            return True
        except Exception as e:
            print(f"Error deleting file {target_file}: {str(e)}")
            return False
            
    return False