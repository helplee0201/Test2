import networkx as nx
import pandas as pd
from pyvis.network import Network
try:
    import community  # python-louvain 패키지
except ImportError:
    print("python-louvain 패키지가 설치되지 않았습니다. pip install python-louvain을 실행하세요.")
    community = None

def find_cycles(graph, lengths):
    cycles = {length: [] for length in lengths}
    for cycle in nx.simple_cycles(graph):
        cycle_length = len(cycle)
        if cycle_length in lengths:
            sorted_cycle = tuple(sorted(cycle))
            if sorted_cycle not in cycles[cycle_length]:
                cycles[cycle_length].append(sorted_cycle)
    return cycles

def filter_paths_of_length_3_or_more(graph):
    filtered_edges = set()
    length_3_plus_edges = set()
    for node in graph.nodes():
        for path_length in range(3, len(graph.nodes()) + 1):
            for path in nx.all_simple_paths(graph, source=node, target=node, cutoff=path_length):
                if len(path) >= 3:
                    for i in range(len(path) - 1):
                        edge = (path[i], path[i + 1])
                        filtered_edges.add(edge)
                        length_3_plus_edges.add(edge)
    return nx.DiGraph(filtered_edges), length_3_plus_edges

def split_into_subgraphs(graph, num_subgraphs=3):
    if community is None:
        print("Louvain 커뮤니티 감지가 불가능합니다. 노드 수 기반으로 분할합니다.")
        nodes = list(graph.nodes())
        nodes_per_subgraph = len(nodes) // num_subgraphs
        subgraphs = []
        for i in range(num_subgraphs):
            start_idx = i * nodes_per_subgraph
            end_idx = start_idx + nodes_per_subgraph if i < num_subgraphs - 1 else len(nodes)
            subgraph_nodes = nodes[start_idx:end_idx]
            subgraphs.append(graph.subgraph(subgraph_nodes).copy())
    else:
        partition = community.best_partition(graph.to_undirected())
        clusters = {}
        for node, cluster_id in partition.items():
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(node)
        
        subgraphs = []
        for cluster_id in sorted(clusters.keys()):
            subgraph = graph.subgraph(clusters[cluster_id]).copy()
            subgraphs.append(subgraph)
        
        if len(subgraphs) < num_subgraphs:
            nodes = list(graph.nodes())
            nodes_per_subgraph = len(nodes) // num_subgraphs
            subgraphs = []
            for i in range(num_subgraphs):
                start_idx = i * nodes_per_subgraph
                end_idx = start_idx + nodes_per_subgraph if i < num_subgraphs - 1 else len(nodes)
                subgraph_nodes = nodes[start_idx:end_idx]
                subgraphs.append(graph.subgraph(subgraph_nodes).copy())
    
    while len(subgraphs) < num_subgraphs:
        subgraphs.append(nx.DiGraph())
    
    return subgraphs[:num_subgraphs]

def draw_graph(graph, cycles, lengths, insured_dict, contractor_dict):
    filtered_graph, length_3_plus_edges = filter_paths_of_length_3_or_more(graph)
    
    subgraphs = split_into_subgraphs(filtered_graph if len(filtered_graph.nodes()) > 0 else graph, num_subgraphs=3)
    
    htmls = []
    for i, subgraph in enumerate(subgraphs):
        if subgraph.number_of_nodes() == 0:
            continue
        
        net = Network(notebook=False, directed=True, height='600px', width='100%')
        net.from_nx(subgraph)
        
        # Update node labels with company names
        for node in net.nodes:
            node_id = node['id']
            label = insured_dict.get(node_id, contractor_dict.get(node_id, node_id))
            node['label'] = label
            node['size'] = 30
            node['font'] = {'size': 14}
        
        # Highlight length 3+ edges
        for edge in net.edges:
            u, v = edge['from'], edge['to']
            if (u, v) in length_3_plus_edges:
                edge['color'] = 'red'
                edge['width'] = 3
            else:
                edge['color'] = 'gray'
                edge['width'] = 1
        
        # Highlight cycles
        colors = ['red', 'green', 'blue']
        filtered_cycles = {}
        for length in lengths:
            filtered_cycles[length] = [c for c in cycles[length] if all(node in subgraph.nodes() for node in c)]
        for j, length in enumerate(filtered_cycles):
            for cycle in filtered_cycles[length]:
                if cycle:
                    color = colors[j % len(colors)]
                    for node_id in cycle:
                        for node in net.nodes:
                            if node['id'] == node_id:
                                node['color'] = color
                                break
        
        # Enable physics and arrows
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -3000,
              "springLength": 150
            }
          },
          "edges": {
            "arrows": {
              "to": { "enabled": true, "scaleFactor": 1 }
            }
          }
        }
        """)
        
        htmls.append(net.generate_html())
    
    return htmls

def generate_csv(cycles, lengths):
    csv_files = []
    for length in lengths:
        filename = f'cycles_length_{length}.csv'
        df = pd.DataFrame(cycles[length], columns=[f"Node{i+1}" for i in range(length)])
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        csv_files.append((filename, csv_data))
    return csv_files