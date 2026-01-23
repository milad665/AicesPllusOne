import os
import glob
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class DocChunk:
    file_path: str
    content: str
    metadata: Dict[str, Any]

class DocumentationStore:
    def __init__(self, root_paths: List[str] = None):
        """
        Initialize the Documentation Store.
        
        Args:
            root_paths: List of root directories to index.
        """
        self.root_paths = root_paths or []
        self.chunks: List[DocChunk] = []

    def index_files(self, paths: List[str] = None):
        """
        Index Markdown files from the specified paths or default roots.
        """
        target_paths = paths or self.root_paths
        
        for root in target_paths:
            # Find all markdown files recursively
            md_files = glob.glob(os.path.join(root, "**/*.md"), recursive=True)
            
            for file_path in md_files:
                self._process_file(file_path)
                
    def _process_file(self, file_path: str):
        """
        Read and chunk a single markdown file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple chunking: Treat the whole file as one context for now,
            # or split by major headers if it gets too big.
            # Ideally, we'd use a markdown parser to split by H1/H2.
            # For MVP, we store the whole file content.
            
            chunk = DocChunk(
                file_path=file_path,
                content=content,
                metadata={
                    "filename": os.path.basename(file_path),
                    "size": len(content)
                }
            )
            self.chunks.append(chunk)
            
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Simple keyword/relevance search.
        
        Args:
            query: Search string
            limit: Max results
            
        Returns:
            List of matching chunks with 'score' and 'path'
        """
        results = []
        query_terms = query.lower().split()
        
        for chunk in self.chunks:
            score = 0
            content_lower = chunk.content.lower()
            path_lower = chunk.file_path.lower()
            
            # Simple scoring
            for term in query_terms:
                if term in content_lower:
                    score += 1
                if term in path_lower:
                    score += 2 # Boost matches in filename
            
            if score > 0:
                results.append({
                    "score": score,
                    "file_path": chunk.file_path,
                    "content": chunk.content[:1000] + "..." if len(chunk.content) > 1000 else chunk.content,
                    "metadata": chunk.metadata
                })
        
        # Sort by score desc
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
