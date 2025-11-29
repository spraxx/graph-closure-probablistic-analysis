import networkx as nx
import os

class GraphLoader:
    """Handles loading of graphs from various file formats."""

    @staticmethod
    def load_sw_format(filepath: str) -> nx.DiGraph:
        """
        Parses the specific SW text format:
        Skipping first 2 lines, then NumNodes, NumEdges, then Edge List.
        """
        G = nx.DiGraph()
        with open(filepath, 'r') as f:
            lines = f.read().splitlines()
        
        try:
            # Based on SWtinyG.txt snippet
            # Line 0, 1: Metadata/Ignored
            num_vertices = int(lines[2])
            # num_edges = int(lines[3]) # Redundant for parsing but good for validation
            
            # Add all nodes to ensure isolated ones are included
            G.add_nodes_from(range(num_vertices))
            
            # Parse edges starting from line 4
            for line in lines[4:]:
                parts = list(map(int, line.split()))
                if len(parts) == 2:
                    u, v = parts
                    G.add_edge(u, v)
                    
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse SW format file {filepath}: {e}")
            
        return G

    @staticmethod
    def load_graph(filepath: str) -> nx.DiGraph:
        if filepath.endswith('.gml'):
            return nx.read_gml(filepath)
        elif filepath.endswith('.txt'):
            return GraphLoader.load_sw_format(filepath)
        else:
            raise ValueError(f"Unsupported file extension: {filepath}")