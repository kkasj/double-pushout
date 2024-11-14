import os
import json
from datetime import datetime

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