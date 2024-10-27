import dash
from dash import html, dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, Output, State, ALL
import networkx as nx
import json
import uuid

class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.elements = []
    
    @classmethod
    def from_elements(cls, elements):
        manager = cls()
        manager.elements = elements

        manager.graph = nx.Graph()
        for element in elements:
            if 'source' in element['data']:
                manager.graph.add_edge(element['data']['source'], element['data']['target'], id=element['data']['id'])
            else:
                manager.graph.add_node(element['data']['id'])

        return manager

    
    @classmethod
    def from_dict(cls, data):
        """Create a GraphManager instance from a dictionary.
        
        Parameters
        ----------
        data : dict
            Dictionary containing graph data.
        """
        manager = cls()
        if not data:
            return manager
            
        # Restore elements
        manager.elements = data.get('elements', [])
        
        # Rebuild NetworkX graph
        for element in manager.elements:
            # TODO
            if 'id' in element['data']:
                manager.graph.add_node(element['data']['id'])
            elif 'source' in element['data']:
                manager.graph.add_edge(element['data']['source'], 
                                     element['data']['target'])
        return manager
        
    def to_dict(self):
        """Convert the graph manager to a dictionary.
        
        Returns
        -------
        dict
            Dictionary containing graph data.
        """
        return {
            'elements': self.elements,
            'graph': {
                'nodes': list(self.graph.nodes()),
                'edges': [f"{u}-{v}" for u, v in self.graph.edges()]
            }
        }
        
    def add_node(self, node_id, **attrs):
        """Add a node to the graph and the elements list.

        Parameters
        ----------
        node_id : str
            The node ID.
        """        
        self.graph.add_node(node_id, **attrs)
        self.elements.append({
            'data': {'id': node_id, 'label': node_id},
        })
        
    def add_edge(self, source, target):
        """Add an edge to the graph and the elements list.

        Parameters
        ----------
        source : str
            The source node ID.
        target : str
            The target node ID.
        """        
        if source in self.graph.nodes() and target in self.graph.nodes():
            edge_id = f"{source}-{target}"
            self.graph.add_edge(source, target)
            self.elements.append({
                'data': {
                    'id': edge_id,
                    'source': source,
                    'target': target
                }
            })
            
    def remove_elements(self, selected_nodes=None, selected_edges=None, k_elements=None):
        """Remove nodes and edges from the graph and the elements list.

        Parameters
        ----------
        selected_nodes : list, optional
            The selected nodes.
        selected_edges : list, optional
            The selected edges.
        k_elements : dict, optional
            Dictionary containing K nodes and edges that should not be removed.
        """        
        if not selected_nodes and not selected_edges:
            return

        # Filter out K elements from selected nodes and edges

        selected_node_ids = set()
        if selected_nodes:
            for node in selected_nodes:
                if k_elements and node['id'] in k_elements.get('nodes', []):
                    continue
                selected_node_ids.add(node['id'])
        
        selected_edge_ids = set()
        if selected_edges:
            for edge in selected_edges:
                if k_elements and f"{edge['source']}-{edge['target']}" in k_elements.get('edges', []):
                    continue
                selected_edge_ids.add(f"{edge['source']}-{edge['target']}")

        new_node_elements = []
        new_edge_elements = []
        current_node_elements = [e for e in self.elements if 'source' not in e['data']]
        current_edge_elements = [e for e in self.elements if 'source' in e['data']]

        # Remove nodes
        for e in current_node_elements:
            if e['data']['id'] not in selected_node_ids:
                new_node_elements.append(e)
            else:
                self.graph.remove_node(e['data']['id'])

        # Remove edges
        new_node_ids = [e['data']['id'] for e in new_node_elements]
        for e in current_edge_elements:
            source, target = e['data']['source'], e['data']['target']
            if f"{source}-{target}" not in selected_edge_ids and f"{target}-{source}" not in selected_edge_ids and source in new_node_ids and target in new_node_ids:
                new_edge_elements.append(e)
            # Remove edge in the NetworkX graph if it still exists
            elif self.graph.has_edge(source, target):
                self.graph.remove_edge(source, target)
        
        self.elements = new_node_elements + new_edge_elements

    
    def clear(self):
        """Clear the graph and the elements list.
        """        
        self.graph.clear()
        self.elements = []
    
    def copy_from(self, elements):
        """Copy the elements to the graph and the elements list.

        Parameters
        ----------
        elements : list
            The elements to copy.
        """        
        self.clear()

        node_elements = [e for e in elements if 'source' not in e['data']]
        edge_elements = [e for e in elements if 'source' in e['data']]

        for element in node_elements:
            self.add_node(element['data']['id'])

        for element in edge_elements:
            self.add_edge(element['data']['source'], element['data']['target'])

class RuleManager:
    def __init__(self):
        self.id = str(uuid.uuid4())
        print(f"Created new RuleManager with id: {self.id}")
        self.lhs = GraphManager()
        self.rhs = GraphManager()
        self.k = GraphManager()
    
    @classmethod
    def from_dict(cls, data):
        if not data:
            return cls()  # Return empty RuleManager if no data
        rule_manager = cls()
        rule_manager.lhs.copy_from(data.get('lhs', []))
        rule_manager.rhs.copy_from(data.get('rhs', []))
        k_data = data.get('k', {'nodes': [], 'edges': []})
        for node in k_data['nodes']:
            rule_manager.k.add_node(node)
        for edge in k_data['edges']:
            source, target = edge.split('-')
            rule_manager.k.add_edge(source, target)
        rule_manager.id = data['id']
        return rule_manager

    def to_dict(self):
        return {
            'id': self.id,
            'lhs': self.lhs.elements,
            'rhs': self.rhs.elements,
            'k': {
                'nodes': list(self.k.graph.nodes()),
                'edges': [f"{u}-{v}" for u, v in self.k.graph.edges()]
            }
    }
        
    @classmethod
    def initialize_from_selection(cls, selected_nodes, selected_edges):
        """Initialize the LHS and RHS graphs from the selected nodes and edges.

        Parameters
        ----------
        selected_nodes : list
            The selected nodes.
        selected_edges : list
            The selected edges.
        """        
        rule = cls()
        
        # Add selected nodes
        if selected_nodes:
            for node in selected_nodes:
                rule.lhs.add_node(node['id'])
                rule.rhs.add_node(node['id'])
        
        # Add selected edges
        if selected_edges:
            for edge in selected_edges:
                if edge['source'] in rule.lhs.graph.nodes() and edge['target'] in rule.lhs.graph.nodes():
                    rule.lhs.add_edge(edge['source'], edge['target'])
                    rule.rhs.add_edge(edge['source'], edge['target'])
        
        print(rule.lhs.elements, rule.rhs.elements)
        
        # Ensure all elements start with no K highlighting
        for element in rule.lhs.elements:
            element['classes'] = ''
        for element in rule.rhs.elements:
            element['classes'] = ''
        
        return rule
    
    def update_k_elements(self, selected_nodes, selected_edges):
        """Update the k elements from the selected nodes and edges.

        Parameters
        ----------
        selected_nodes : list
            The selected nodes.
        selected_edges : list
            The selected edges.
        """        
        self.k.clear()
        
        # Add selected nodes to K
        if selected_nodes:
            for node in selected_nodes:
                if node['id'] in self.lhs.graph.nodes() and node['id'] in self.rhs.graph.nodes():
                    self.k.add_node(node['id'])
        
        # Add selected edges to K
        if selected_edges:
            for edge in selected_edges:
                source, target = edge['source'], edge['target']
                if (source in self.k.graph.nodes() and 
                    target in self.k.graph.nodes() and 
                    self.lhs.graph.has_edge(source, target) and 
                    self.rhs.graph.has_edge(source, target)):
                    self.k.add_edge(source, target)
        
        print("K nodes and edges:")
        print(self.k.graph.nodes())
        print(self.k.graph.edges())

    
    def highlight_k_elements(self):
        """Update the visualization to highlight K elements in both LHS and RHS."""
        k_nodes = set(self.k.graph.nodes())
        
        # Update LHS elements
        for element in self.lhs.elements:
            edge_element = 'source' in element['data']
            if (edge_element and self.k.graph.has_edge(element['data']['source'], element['data']['target'])) or (not edge_element and element['data']['id'] in k_nodes):
                element['classes'] = 'k-element'
            else:
                element['classes'] = ''
        
        # Update RHS elements
        for element in self.rhs.elements:
            edge_element = 'source' in element['data']
            if (edge_element and self.k.graph.has_edge(element['data']['source'], element['data']['target'])) or (not edge_element and element['data']['id'] in k_nodes):
                element['classes'] = 'k-element'
            else:
                element['classes'] = ''
    
    def reset_rhs_to_lhs(self):
        """Reset the RHS graph to match the LHS graph."""
        self.rhs.clear()
        self.rhs.copy_from(self.lhs.elements)