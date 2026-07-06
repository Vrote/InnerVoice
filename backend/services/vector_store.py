# backend/services/vector_store.py
import os
import logging

logger = logging.getLogger(__name__)

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("chromadb is not installed. Using in-memory mock client fallback for vector operations.")

    class MockCollection:
        def __init__(self, name):
            self.name = name
            self._data = {}

        def count(self):
            return len(self._data)

        def add(self, ids, embeddings, documents, metadatas=None):
            metadatas = metadatas or [{}] * len(documents)
            for idx, (i, doc) in enumerate(zip(ids, documents)):
                meta = metadatas[idx] if idx < len(metadatas) else {}
                self._data[i] = {
                    "document": doc,
                    "metadata": meta
                }

        def delete(self, ids):
            for i in ids:
                if i in self._data:
                    del self._data[i]

        def query(self, query_embeddings, n_results=5):
            # Simple fallback: return the most recently added items up to n_results
            items = list(self._data.items())
            selected = items[-n_results:] if n_results > 0 else []
            return {
                "ids": [[x[0] for x in selected]],
                "documents": [[x[1]["document"] for x in selected]],
                "metadatas": [[x[1]["metadata"] for x in selected]]
            }

    class MockClient:
        def __init__(self, path):
            self.path = path
            self._collections = {}

        def get_or_create_collection(self, name):
            if name not in self._collections:
                self._collections[name] = MockCollection(name)
            return self._collections[name]

from backend.core.config import settings
from backend.services.embedding_service import embed_text



# Initialize ChromaDB Persistent Client (or Mock Fallback)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
if CHROMA_AVAILABLE:
    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
else:
    chroma_client = MockClient(path=settings.CHROMA_PERSIST_DIR)

def get_memories_collection(user_id: str):
    # Chroma collection names must be 3-63 chars, start/end with alphanumeric, contain alphanumeric, _, - and no consecutive dots
    safe_name = f"user_{user_id}_memories".replace("-", "_")
    return chroma_client.get_or_create_collection(name=safe_name)

def get_entries_collection(user_id: str):
    safe_name = f"user_{user_id}_entries".replace("-", "_")
    return chroma_client.get_or_create_collection(name=safe_name)

async def add_memory_to_vector_store(user_id: str, memory_id: str, memory_text: str, memory_type: str, importance: float):
    try:
        embedding = await embed_text(memory_text)
        collection = get_memories_collection(user_id)
        collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[memory_text],
            metadatas=[{"memory_type": memory_type, "importance_score": importance}]
        )
        logger.info(f"Added memory {memory_id} to vector store for user {user_id}")
    except Exception as e:
        logger.error(f"Error adding memory to vector store: {e}")

async def delete_memory_from_vector_store(user_id: str, memory_id: str):
    try:
        collection = get_memories_collection(user_id)
        collection.delete(ids=[memory_id])
        logger.info(f"Deleted memory {memory_id} from vector store for user {user_id}")
    except Exception as e:
        logger.error(f"Error deleting memory from vector store: {e}")

async def query_memories_vector_store(user_id: str, query_text: str, limit: int = 5) -> list:
    try:
        embedding = await embed_text(query_text)
        collection = get_memories_collection(user_id)
        
        # Check if collection is empty
        if collection.count() == 0:
            return []
            
        results = collection.query(
            query_embeddings=[embedding],
            n_results=min(limit, collection.count()),
        )
        
        memories = []
        if results and 'documents' in results and results['documents']:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(documents)
            ids = results['ids'][0]
            for doc, meta, mid in zip(documents, metadatas, ids):
                memories.append({
                    "id": mid,
                    "text": doc,
                    "type": meta.get("memory_type", "context"),
                    "importance": meta.get("importance_score", 0.5)
                })
        return memories
    except Exception as e:
        logger.error(f"Error querying memories vector store: {e}")
        return []

async def add_entry_to_vector_store(user_id: str, entry_id: str, entry_text: str, date_str: str, emotion: str):
    try:
        embedding = await embed_text(entry_text)
        collection = get_entries_collection(user_id)
        collection.add(
            ids=[entry_id],
            embeddings=[embedding],
            documents=[entry_text],
            metadatas=[{"date": date_str, "emotion": emotion}]
        )
        logger.info(f"Added entry {entry_id} to vector store for user {user_id}")
    except Exception as e:
        logger.error(f"Error adding entry to vector store: {e}")

async def query_entries_vector_store(user_id: str, query_text: str, limit: int = 3) -> list:
    try:
        embedding = await embed_text(query_text)
        collection = get_entries_collection(user_id)
        
        if collection.count() == 0:
            return []

        results = collection.query(
            query_embeddings=[embedding],
            n_results=min(limit, collection.count()),
        )
        
        entries = []
        if results and 'documents' in results and results['documents']:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(documents)
            ids = results['ids'][0]
            for doc, meta, eid in zip(documents, metadatas, ids):
                entries.append({
                    "id": eid,
                    "content": doc,
                    "date": meta.get("date", ""),
                    "emotion": meta.get("emotion", "neutral")
                })
        return entries
    except Exception as e:
        logger.error(f"Error querying entries vector store: {e}")
        return []
