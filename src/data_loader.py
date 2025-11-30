import networkx as nx
import os

class GraphLoader:
    """Handles loading of graphs from various file formats."""

    @staticmethod
    def load_sw_format(filepath: str) -> nx.DiGraph:
        """Parses the specific SW text format."""
        G = nx.DiGraph()
        with open(filepath, 'r') as f:
            lines = f.read().splitlines()
        
        try:
            num_vertices = int(lines[2])
            G.add_nodes_from(range(num_vertices))
            for line in lines[4:]:
                parts = list(map(int, line.split()))
                if len(parts) == 2:
                    G.add_edge(parts[0], parts[1])
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse SW format file {filepath}: {e}")
            
        return G

    @staticmethod
    def load_snap_format(filepath: str) -> nx.DiGraph:
        """
        Parses Stanford SNAP format.
        - Skips lines starting with '#'
        - Reads 'u v' (tab or space separated)
        """
        G = nx.DiGraph()
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                parts = line.strip().split()
                if len(parts) >= 2:
                    u, v = int(parts[0]), int(parts[1])
                    G.add_edge(u, v)
        return G

    @staticmethod
    def load_graph(filepath: str) -> nx.DiGraph:
        filename = os.path.basename(filepath)
        
        if filename.endswith('.gml'):
            return nx.read_gml(filepath)
        elif filename.startswith('SW') and filename.endswith('.txt'):
            return GraphLoader.load_sw_format(filepath)
        # Assuming SNAP files might be .txt but don't start with SW, 
        # or we explicitly check for known SNAP filenames
        elif 'web-' in filename or 'wiki-' in filename or 'email-' in filename:
             return GraphLoader.load_snap_format(filepath)
        elif filepath.endswith('.txt'):
            # Fallback: try SW, if fail, try SNAP? 
            # Safest is to default to SW for this project unless specified.
            try:
                return GraphLoader.load_sw_format(filepath)
            except:
                return GraphLoader.load_snap_format(filepath)
        else:
            raise ValueError(f"Unsupported file extension: {filepath}")