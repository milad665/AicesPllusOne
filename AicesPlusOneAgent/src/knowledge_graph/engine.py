import networkx as nx
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class KnowledgeGraphEngine:
    """
    Knowledge Graph Engine powering the Aices+1 Agent.
    
    Current Implementation:
    - Uses NetworkX (in-memory) for graph operations.
    - Persists to local JSON files per tenant.
    - Supports multi-tenancy via tenant_id isolation.
    """
    
    def __init__(self, storage_dir: str = "data/knowledge_graphs"):
        """
        Initialize the Knowledge Graph Engine.
        
        Args:
            storage_dir: Base directory to store tenant graphs.
        """
        self.storage_dir = storage_dir
        self.graphs: Dict[str, nx.MultiDiGraph] = {}
        
        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def _get_graph(self, tenant_id: str) -> nx.MultiDiGraph:
        """
        Get or load the graph for a specific tenant.
        """
        if tenant_id not in self.graphs:
            self.graphs[tenant_id] = self._load_graph(tenant_id)
        return self.graphs[tenant_id]
        
    def _load_graph(self, tenant_id: str) -> nx.MultiDiGraph:
        """Load tenant graph from disk or create new."""
        file_path = os.path.join(self.storage_dir, f"{tenant_id}.json")
        G = nx.MultiDiGraph()
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                # Reconstruct graph from node-link data
                G = nx.node_link_graph(data)
            except Exception as e:
                print(f"Error loading graph for tenant {tenant_id}: {e}")
                # Return empty graph on failure
        return G

    def _save_graph(self, tenant_id: str):
        """Persist tenant graph to disk."""
        if tenant_id in self.graphs:
            G = self.graphs[tenant_id]
            data = nx.node_link_data(G)
            file_path = os.path.join(self.storage_dir, f"{tenant_id}.json")
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

    def add_node(self, tenant_id: str, node_id: str, label: str, properties: Dict[str, Any] = None):
        """
        Add a node to the tenant's graph.
        
        Args:
            tenant_id: The tenant identifier.
            node_id: Unique ID for the node within the tenant (e.g., 'standard:123').
            label: Node type/label (e.g., 'Standard', 'Component', 'Document').
            properties: Additional attributes.
        """
        G = self._get_graph(tenant_id)
        properties = properties or {}
        properties['label'] = label
        properties['updated_at'] = datetime.now().isoformat()
        
        G.add_node(node_id, **properties)
        self._save_graph(tenant_id)

    def add_edge(self, tenant_id: str, source_id: str, target_id: str, relation: str, properties: Dict[str, Any] = None):
        """
        Add an edge (relationship) between two nodes.
        """
        G = self._get_graph(tenant_id)
        properties = properties or {}
        properties['relation'] = relation
        properties['updated_at'] = datetime.now().isoformat()
        
        G.add_edge(source_id, target_id, key=relation, **properties)
        self._save_graph(tenant_id)
        
    def search_nodes(self, tenant_id: str, label: str = None, property_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for nodes in the tenant's graph.
        
        Args:
            tenant_id: Tenant ID.
            label: Filter by node label (optional).
            property_filter: Key-value pairs matching node properties (exact match).
            
        Returns:
            List of node data dictionaries.
        """
        G = self._get_graph(tenant_id)
        results = []
        
        for node_id, data in G.nodes(data=True):
            # Label filter
            if label and data.get('label') != label:
                continue
                
            # Property filter
            if property_filter:
                match = True
                for k, v in property_filter.items():
                    if data.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            
            # Add to results with ID
            node_data = data.copy()
            node_data['id'] = node_id
            results.append(node_data)
            
        return results

    def semantic_search(self, tenant_id: str, query: str, label: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a simple keyword-based 'semantic' search on node properties.
        (Upgrade to Vector Embedding search later).
        """
        G = self._get_graph(tenant_id)
        results = []
        query_terms = query.lower().split()
        
        for node_id, data in G.nodes(data=True):
            if label and data.get('label') != label:
                continue
                
            score = 0
            # Search across all string properties
            content_blob = " ".join([str(v).lower() for v in data.values() if isinstance(v, str)])
            
            for term in query_terms:
                if term in content_blob:
                    score += 1
            
            if score > 0:
                node_data = data.copy()
                node_data['id'] = node_id
                node_data['score'] = score
                results.append(node_data)
                
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
