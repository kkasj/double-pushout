from datetime import datetime

def get_default_graph_layout():
    timestamp = datetime.now().isoformat()
    return {
        'name': 'breadthfirst',
        'animate': True,
        'animationDuration': 200,
        'fit': True,
        'padding': 50,
        'randomization': timestamp,  # Add timestamp to make each update unique
    }