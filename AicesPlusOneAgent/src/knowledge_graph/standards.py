from typing import List, Dict, Any, Optional
import uuid
from .engine import KnowledgeGraphEngine

class StandardsManager:
    """
    Manages Coding Standards and Best Practices within the Knowledge Graph.
    """
    
    def __init__(self, engine: KnowledgeGraphEngine):
        self.engine = engine
        
    def add_standard(self, tenant_id: str, description: str, type: str, category: str, tags: List[str] = None) -> str:
        """
        Add a coding standard to the knowledge base.
        
        Args:
            tenant_id: Tenant ID.
            description: The standard rule or practice description.
            type: 'good_practice' or 'bad_practice'.
            category: 'python', 'security', 'performance', etc.
            tags: List of related keywords.
        """
        standard_id = f"standard:{uuid.uuid4()}"
        
        properties = {
            "description": description,
            "type": type,
            "category": category,
            "tags": tags or []
        }
        
        self.engine.add_node(
            tenant_id=tenant_id, 
            node_id=standard_id, 
            label="Standard", 
            properties=properties
        )
        return standard_id

    def search_standards(self, tenant_id: str, query: str = None, category: str = None) -> List[Dict[str, Any]]:
        """
        Search for coding standards.
        """
        if query:
            # Semantic/Keyword search
            results = self.engine.semantic_search(tenant_id, query, label="Standard")
            if category:
                results = [r for r in results if r.get('category') == category]
            return results
        else:
            # Filter search
            filters = {}
            if category:
                filters['category'] = category
            return self.engine.search_nodes(tenant_id, label="Standard", property_filter=filters)
