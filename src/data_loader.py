import networkx as nx
import os
from typing import Union


class GraphLoader:
    """Handles loading of graphs from various file formats."""
    
    @staticmethod
    def load_sw_format(filepath: str) -> nx.DiGraph:
        """
        Parse a directed graph from the SW text format.
        
        The SW format expects:
        - Line 0-1: Header information (ignored)
        - Line 2: Number of vertices (integer)
        - Line 3: Header (ignored)
        - Lines 4+: Edges as "u v" (space-separated integers)
        
        Args:
            filepath: Path to the SW format file.
        
        Returns:
            A directed graph (nx.DiGraph) with parsed nodes and edges.
        
        Raises:
            ValueError: If the file cannot be parsed or has invalid format.
        """
        G: nx.DiGraph = nx.DiGraph()
        with open(filepath, 'r') as f:
            lines: list[str] = f.read().splitlines()
        
        try:
            num_vertices: int = int(lines[2])
            G.add_nodes_from(range(num_vertices))
            for line in lines[4:]:
                parts: list[int] = list(map(int, line.split()))
                if len(parts) == 2:
                    G.add_edge(parts[0], parts[1])
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse SW format file {filepath}: {e}")
            
        return G
    
    @staticmethod
    def load_snap_format(filepath: str) -> nx.DiGraph:
        """
        Parse a directed graph from the Stanford SNAP format.
        
        The SNAP format expects:
        - Lines starting with '#': Comments (skipped)
        - Other lines: Edges as "u v" (tab or space-separated integers)
        
        Args:
            filepath: Path to the SNAP format file.
        
        Returns:
            A directed graph (nx.DiGraph) with parsed edges.
        """
        G: nx.DiGraph = nx.DiGraph()
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                parts: list[str] = line.strip().split()
                if len(parts) >= 2:
                    u: int = int(parts[0])
                    v: int = int(parts[1])
                    G.add_edge(u, v)
        return G
    
    @staticmethod
    def load_graph(filepath: str) -> nx.DiGraph:
        """
        Load a directed graph from a file, automatically detecting the format.
        
        Supported formats:
        - GML: Files ending with '.gml'
        - SW: Files starting with 'SW' and ending with '.txt'
        - SNAP: Files containing 'web-', 'wiki-', or 'email-' in filename
        - TXT (fallback): Other '.txt' files (tries SW format first, then SNAP)
        
        Args:
            filepath: Path to the graph file.
        
        Returns:
            A directed graph (nx.DiGraph) parsed from the file.
        
        Raises:
            ValueError: If the file format is not supported.
        """
        filename: str = os.path.basename(filepath)
        
        if filename.endswith('.gml'):
            return nx.read_gml(filepath)
        elif filename.startswith('SW') and filename.endswith('.txt'):
            return GraphLoader.load_sw_format(filepath)
        elif 'web-' in filename or 'wiki-' in filename or 'email-' in filename:
            return GraphLoader.load_snap_format(filepath)
        elif filepath.endswith('.txt'):
            try:
                return GraphLoader.load_sw_format(filepath)
            except Exception:
                return GraphLoader.load_snap_format(filepath)
        else:
            raise ValueError(f"Unsupported file extension: {filepath}")