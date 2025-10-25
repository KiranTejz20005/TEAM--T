"""
RAG (Retrieval-Augmented Generation) service for document context retrieval.
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime

from app.config import settings


class RAGService:
    """Service for document retrieval and context generation."""
    
    def __init__(self):
        """Initialize RAG service with ChromaDB and embeddings."""
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="financial_documents",
            metadata={"description": "Financial document embeddings for FinMDA-Bot"}
        )
    
    async def index_document(self, document_id: int, content: str, metadata: Dict[str, Any]) -> bool:
        """Index a document for retrieval."""
        try:
            # Split content into chunks
            chunks = self._chunk_text(content)
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            # Prepare metadata for each chunk
            chunk_metadata = []
            chunk_ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata.append({
                    "document_id": document_id,
                    "chunk_index": i,
                    "chunk_length": len(chunk),
                    **metadata
                })
                chunk_ids.append(f"doc_{document_id}_chunk_{i}")
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            return True
            
        except Exception as e:
            print(f"Error indexing document {document_id}: {str(e)}")
            return False
    
    async def retrieve_context(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        top_k: int = 5
    ) -> str:
        """Retrieve relevant context for a query."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Build where clause for filtering
            where_clause = {}
            if document_id:
                where_clause["document_id"] = document_id
            
            # Query collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                where=where_clause if where_clause else None
            )
            
            # Format context
            context_parts = []
            citations = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                context_parts.append(f"[Context {i+1}]: {doc}")
                citations.append({
                    "document_id": metadata.get("document_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "relevance_score": 1 - distance,
                    "source": f"Document {metadata.get('document_id')}, Chunk {metadata.get('chunk_index')}"
                })
            
            context = "\n\n".join(context_parts)
            
            return context
            
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return ""
    
    async def retrieve_with_citations(
        self, 
        query: str, 
        document_id: Optional[int] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Retrieve context with detailed citation information."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Build where clause for filtering
            where_clause = {}
            if document_id:
                where_clause["document_id"] = document_id
            
            # Query collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                where=where_clause if where_clause else None
            )
            
            # Format results
            context_parts = []
            citations = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                relevance_score = 1 - distance
                
                context_parts.append(f"[Context {i+1}]: {doc}")
                citations.append({
                    "document_id": metadata.get("document_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "relevance_score": relevance_score,
                    "source": f"Document {metadata.get('document_id')}, Chunk {metadata.get('chunk_index')}",
                    "content": doc[:200] + "..." if len(doc) > 200 else doc
                })
            
            context = "\n\n".join(context_parts)
            
            return {
                "context": context,
                "citations": citations,
                "total_results": len(results['documents'][0]),
                "query": query
            }
            
        except Exception as e:
            print(f"Error retrieving context with citations: {str(e)}")
            return {
                "context": "",
                "citations": [],
                "total_results": 0,
                "query": query
            }
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def search_similar_documents(
        self, 
        query: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar documents across all indexed content."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Query collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            # Group by document
            document_scores = {}
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                doc_id = metadata.get("document_id")
                relevance_score = 1 - distance
                
                if doc_id not in document_scores:
                    document_scores[doc_id] = {
                        "document_id": doc_id,
                        "max_relevance": relevance_score,
                        "chunks": [],
                        "total_chunks": 0
                    }
                
                document_scores[doc_id]["chunks"].append({
                    "content": doc,
                    "relevance_score": relevance_score,
                    "chunk_index": metadata.get("chunk_index")
                })
                document_scores[doc_id]["total_chunks"] += 1
                document_scores[doc_id]["max_relevance"] = max(
                    document_scores[doc_id]["max_relevance"], 
                    relevance_score
                )
            
            # Sort by relevance
            similar_docs = sorted(
                document_scores.values(),
                key=lambda x: x["max_relevance"],
                reverse=True
            )
            
            return similar_docs
            
        except Exception as e:
            print(f"Error searching similar documents: {str(e)}")
            return []
    
    async def delete_document(self, document_id: int) -> bool:
        """Delete all chunks for a document."""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                # Delete chunks
                self.collection.delete(ids=results['ids'])
            
            return True
            
        except Exception as e:
            print(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "embedding_model": settings.embedding_model
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_chunks": 0
            }
