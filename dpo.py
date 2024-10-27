import networkx as nx
from itertools import combinations

def match_subgraph(host_graph, lhs_graph):
    """
    Find all subgraph isomorphisms from lhs_graph to host_graph.

    Parameters
    ----------
    host_graph : networkx.Graph
        The host graph G.
    lhs_graph : networkx.Graph
        The left-hand side graph L of the rule.

    Returns
    -------
    List[Dict]
        A list of node mappings where each mapping is a dict from LHS nodes to host graph nodes.
    """
    matcher = nx.algorithms.isomorphism.GraphMatcher(host_graph, lhs_graph)
    l = [{v: k for k, v in match.items()} for match in matcher.subgraph_isomorphisms_iter()]
    print(l)
    return l

def apply_dpo_rule(host_graph_manager, rule_manager, match):
    """
    Apply a single DPO rule to the host graph.

    Parameters
    ----------
    host_graph_manager : GraphManager
        The host graph manager.
    rule_manager : RuleManager
        The rule to apply.
    match : Dict
        The mapping from LHS nodes to host graph nodes.

    Returns
    -------
    bool
        True if the rule was applied successfully, False otherwise.
    """
    try:
        G = host_graph_manager.graph
        L = rule_manager.lhs.graph
        K = rule_manager.k.graph
        R = rule_manager.rhs.graph

        # 1. Check gluing condition
        # Identify nodes that would be dangling
        nodes_to_remove = set(n for n in L.nodes() if n not in K.nodes())
        for node in nodes_to_remove:
            matched_node = match[node]
            # Check for dangling edges
            neighbors = set(G.neighbors(matched_node))
            matched_l_neighbors = {match[n] for n in L.neighbors(node) if n in match}
            if neighbors - matched_l_neighbors:
                print(f"Dangling edge found for node {node}")
                return False

        # 2. Remove elements (L - K)
        # Remove edges first
        edges_to_remove = set(L.edges()) - set(K.edges())
        for edge in edges_to_remove:
            source, target = match[edge[0]], match[edge[1]]
            if G.has_edge(source, target):
                G.remove_edge(source, target)
                edge_id = f"{source}-{target}"
                host_graph_manager.elements = [
                    e for e in host_graph_manager.elements 
                    if e['data'].get('id') != edge_id
                ]

        # Remove nodes
        for node in nodes_to_remove:
            matched_node = match[node]
            if matched_node in G:
                G.remove_node(matched_node)
                host_graph_manager.elements = [
                    e for e in host_graph_manager.elements 
                    if e['data'].get('id') != matched_node
                ]

        # 3. Add elements (R - K)
        # Add new nodes
        nodes_to_add = set(R.nodes()) - set(K.nodes())
        new_node_mapping = {}
        for node in nodes_to_add:
            new_node_id = f"n{len(G.nodes()) + 1}"
            new_node_mapping[node] = new_node_id
            G.add_node(new_node_id)
            host_graph_manager.elements.append({
                'data': {'id': new_node_id, 'label': new_node_id}
            })

        # Add new edges
        edges_to_add = set(R.edges()) - set(K.edges())
        for edge in edges_to_add:
            source = new_node_mapping.get(edge[0], match.get(edge[0], edge[0]))
            target = new_node_mapping.get(edge[1], match.get(edge[1], edge[1]))
            
            if not G.has_edge(source, target):
                edge_id = f"{source}-{target}"
                G.add_edge(source, target)
                host_graph_manager.elements.append({
                    'data': {
                        'id': edge_id,
                        'source': source,
                        'target': target
                    }
                })

        return True

    except Exception as e:
        print(f"Error applying DPO rule: {e}")
        return False

def are_matches_independent(G, match1, match2):
    """
    Check if two matches are parallel independent.
    Two matches are parallel independent if neither match deletes elements
    that the other match uses.

    Parameters
    ----------
    G : networkx.Graph
        The host graph
    match1, match2 : Dict
        The mappings from LHS nodes to host graph nodes
    
    Returns
    -------
    bool
        True if matches are parallel independent
    """
    # Convert matches to sets of nodes
    nodes1 = set(match1.values())
    nodes2 = set(match2.values())
    
    # If matches share nodes, they're not independent
    return len(nodes1.intersection(nodes2)) == 0


def apply_rule_parallel(host_graph_manager, rule_manager):
    """
    Apply a DPO rule to all parallel independent matches simultaneously.

    Parameters
    ----------
    host_graph_manager : GraphManager
        The host graph manager
    rule_manager : RuleManager
        The rule to apply

    Returns
    -------
    int
        Number of successful parallel applications
    """
    # Find all possible matches
    matches = match_subgraph(host_graph_manager.graph, rule_manager.lhs.graph)
    if not matches:
        return 0

    # Find maximal set of parallel independent matches
    independent_matches = []
    for match in matches:
        # Check if this match is independent with all selected matches
        is_independent = all(
            are_matches_independent(host_graph_manager.graph, match, m)
            for m in independent_matches
        )
        if is_independent:
            independent_matches.append(match)

    # Apply rule to all independent matches
    successful_applications = 0
    for match in independent_matches:
        if apply_dpo_rule(host_graph_manager, rule_manager, match):
            successful_applications += 1

    return successful_applications