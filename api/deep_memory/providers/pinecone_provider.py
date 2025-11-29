from pinecone import Pinecone
from typing import List, Dict, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


#=======================================================================
# Pinecone provider
#=======================================================================
class PineconeProvider:
    def __init__(self, api_key: str):
        self.pc = Pinecone(api_key=api_key)
        self._initialize_indexes()


    #=======================================================================
    # Initializes Pinecone indexes
    #=======================================================================
    def _initialize_indexes(self):
        existing_indexes = [index.name for index in self.pc.list_indexes()]

        # Dense indexes
        if "deep-memory-memo" not in existing_indexes:
            self.pc.create_index_for_model(
                name="deep-memory-memo",
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "chunk_text"}
                }
            )
        if "deep-memory-page" not in existing_indexes:
            self.pc.create_index_for_model(
                name="deep-memory-page",
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "chunk_text"}
                }
            )

        # Sparse indexes
        if "deep-memory-memo-sparse" not in existing_indexes:
            self.pc.create_index_for_model(
                name="deep-memory-memo-sparse",
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "pinecone-sparse-english-v0",
                    "field_map": {"text": "chunk_text"}
                }
            )
        if "deep-memory-page-sparse" not in existing_indexes:
            self.pc.create_index_for_model(
                name="deep-memory-page-sparse",
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": "pinecone-sparse-english-v0",
                    "field_map": {"text": "chunk_text"}
                }
            )


    #=======================================================================
    # Upserts records into indexes
    #=======================================================================
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def upsert_records(self, index_name: str, records: List[Dict[str, Any]], namespace: str = "deep-memory"):
        index = self.pc.Index(index_name)
        index.upsert_records(records=records, namespace=namespace)


    #=======================================================================
    # Searches indexes with text queries
    #=======================================================================
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def search_text(self, index_name: str, query_text: str, top_k: int = 5, namespace: str = "deep-memory"):
        index = self.pc.Index(index_name)
        results = index.search(
            query={
                "top_k": top_k,
                "inputs": {
                    "text": query_text
                }
            },
            namespace=namespace
        )
        return results


    #=======================================================================
    # Clears and recreates all deep memory indexes
    #=======================================================================
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def clear_all_indexes(self):
        """Delete and recreate all deep memory indexes"""
        index_names = [
            "deep-memory-memo",
            "deep-memory-page", 
            "deep-memory-memo-sparse",
            "deep-memory-page-sparse"
        ]
        
        # Delete existing indexes
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        for index_name in index_names:
            if index_name in existing_indexes:
                self.pc.delete_index(index_name)
        
        # Recreate indexes
        self._initialize_indexes()


    #=======================================================================
    # Performs hybrid search across dense and sparse indexes with reranking
    #=======================================================================
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def hybrid_search(self, query_text: str, dense_index: str, sparse_index: str, top_k: int = 10) -> Dict[str, Any]:
        dense_results = self.search_text(dense_index, query_text, top_k=top_k*2)
        sparse_results = self.search_text(sparse_index, query_text, top_k=top_k*2)
        merged_results = self._merge_search_results(dense_results, sparse_results)
        reranked_results = self._rerank_results(query_text, merged_results, top_n=top_k)

        return {
            "query": query_text,
            "results": reranked_results,
            "total_found": len(merged_results)
        }


    #=======================================================================
    # Merges and deduplicates search results from dense and sparse indexes
    #=======================================================================
    def _merge_search_results(self, dense_results, sparse_results) -> List[Dict[str, Any]]:
        deduped_hits = {hit['_id']: hit for hit in dense_results['result']['hits'] + sparse_results['result']['hits']}.values()
        sorted_hits = sorted(deduped_hits, key=lambda x: x['_score'], reverse=True)
        result = [{
            '_id': hit['_id'],
            'chunk_text': hit['fields']['chunk_text'],
            'files': hit['fields'].get('files', []),
            '_score': hit['_score']
        } for hit in sorted_hits]

        return result


    #=======================================================================
    # Reranks search results using Pinecone's reranking API
    #=======================================================================
    def _rerank_results(self, query_text: str, documents: List[Dict[str, Any]], top_n: int = 10):
        try:
            reranked = self.pc.inference.rerank(
                model="bge-reranker-v2-m3",
                query=query_text,
                documents=documents,
                rank_fields=["chunk_text"],
                top_n=top_n,
                return_documents=True,
                parameters={
                    "truncate": "END"
                }
            )

            return [{
                'id': doc['document']['_id'],
                'text': doc['document']['chunk_text'],
                'files': doc['document'].get('files', []),
                'score': doc['score']
            } for doc in reranked.data]

        except Exception as e:
            print(f"Reranking failed: {e}")
            return [{
                'id': doc['_id'],
                'text': doc['chunk_text'],
                'files': doc.get('files', []),
                'score': doc['_score']
            } for doc in documents[:top_n]]