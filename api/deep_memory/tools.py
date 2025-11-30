from typing import List, Dict, Any
from .providers import PineconeProvider, OpenAIProvider


#=======================================================================
# Tools for agents to interact with Pinecone and OpenAI providers
#=======================================================================
class Tools:
    def __init__(self, pinecone_provider: PineconeProvider, openai_provider: OpenAIProvider):
        self.pinecone_provider = pinecone_provider
        self.openai_provider = openai_provider


    #=======================================================================
    # Executes a tool by name with given parameters
    #
    # Available tools:
    # - "generate_text": Generate text using OpenAI with a given prompt
    # - "describe_image": Generate description for an image URL
    # - "query_image": Ask a specific question about an image URL
    # - "upsert_records": Store records in a Pinecone index
    # - "memo_hybrid_search": Search memo abstracts using hybrid search
    # - "page_hybrid_search": Search page content using hybrid search
    # - "page_vector_search": Search page content using vector search only
    # - "page_keyword_search": Search page content using keyword search only
    #=======================================================================
    def use_tool(self, tool_name: str, **kwargs) -> Any:
        tools = {
            "generate_text": self._generate_text_tool,
            "describe_image": self._describe_image_tool,
            "query_image": self._query_image_tool,
            "upsert_records": self._upsert_records_tool,
            "memo_hybrid_search": self._memo_hybrid_search_tool,
            "page_hybrid_search": self._page_hybrid_search_tool,
            "page_vector_search": self._page_vector_search_tool,
            "page_keyword_search": self._page_keyword_search_tool,
        }

        if tool_name not in tools:
            available_tools = list(tools.keys())
            raise ValueError(f"Unknown tool '{tool_name}'. Available tools: {available_tools}")

        tool_func = tools[tool_name]
        return tool_func(**kwargs)


    #=======================================================================
    # Generate text using OpenAI
    #=======================================================================
    def _generate_text_tool(self, prompt: str) -> str:
        return self.openai_provider.generate_text(prompt)


    #=======================================================================
    # Describes an image from a URL
    #=======================================================================
    def _describe_image_tool(self, image_url: str) -> str:
        return self.openai_provider.describe_image(image_url, "What's in this image?")


    #=======================================================================
    # Asks a specific question about an image
    #=======================================================================
    def _query_image_tool(self, image_url: str, question: str) -> str:
        return self.openai_provider.describe_image(image_url, question)
    

    #=======================================================================
    # Upsert records into a Pinecone index
    #=======================================================================
    def _upsert_records_tool(self, index_name: str, records: List[Dict[str, Any]], namespace: str = "deep-memory") -> None:
        self.pinecone_provider.upsert_records(index_name, records, namespace)


    #=======================================================================
    # Hybrid search tool (calls pinecone provider)
    #=======================================================================
    def _hybrid_search_tool(self, query_text: str, dense_index: str, sparse_index: str, top_k: int = 5):
        return self.pinecone_provider.hybrid_search(query_text, dense_index, sparse_index, top_k)


    #=======================================================================
    # Memo hybrid search tool
    #=======================================================================
    def _memo_hybrid_search_tool(self, query_text: str, top_k: int = 5) -> str:
        search_results = self._hybrid_search_tool(
            query_text=query_text,
            dense_index="deep-memory-memo",
            sparse_index="deep-memory-memo-sparse",
            top_k=top_k
        )

        if not search_results["results"]:
            return "No relevant memory abstracts found."

        # Format as numbered list
        context_lines = []
        for i, result in enumerate(search_results["results"], 1):
            context_lines.append(f"{i}. {result['text']}")

        return "\n".join(context_lines)


    #=======================================================================
    # Page hybrid search tool
    #=======================================================================
    def _page_hybrid_search_tool(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        search_results = self._hybrid_search_tool(
            query_text=query_text,
            dense_index="deep-memory-page",
            sparse_index="deep-memory-page-sparse",
            top_k=top_k
        )

        if not search_results["results"]:
            return []

        results = []
        for result in search_results["results"]:
            results.append({
                "text": result['text'],
                "files": result.get('files', [])
            })

        return results


    #=======================================================================
    # Search text helper
    #=======================================================================
    def _search_text(self, index_name: str, query_text: str, top_k: int = 5):
        return self.pinecone_provider.search_text(index_name, query_text, top_k)


    #=======================================================================
    # Page vector search tool
    #=======================================================================
    def _page_vector_search_tool(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        search_results = self._search_text("deep-memory-page", query_text, top_k=top_k)

        if not search_results["result"]["hits"]:
            return []

        results = []
        for hit in search_results["result"]["hits"]:
            results.append({
                "text": hit['fields']['chunk_text'],
                "files": hit['fields'].get('files', [])
            })

        return results


    #=======================================================================
    # Page keyword search tool
    #=======================================================================
    def _page_keyword_search_tool(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        search_results = self._search_text("deep-memory-page-sparse", query_text, top_k=top_k)

        if not search_results["result"]["hits"]:
            return []

        results = []
        for hit in search_results["result"]["hits"]:
            results.append({
                "text": hit['fields']['chunk_text'],
                "files": hit['fields'].get('files', [])
            })

        return results

