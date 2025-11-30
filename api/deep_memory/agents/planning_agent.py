from typing import Dict, List, Any
import json
import re
import textwrap
from ..tools import Tools


#=======================================================================
# Agent for planning deep memory searches
#=======================================================================
class PlanningAgent:
    def __init__(self, tools: Tools):
        self.tools = tools


    #=======================================================================
    # Plans a deep memory search
    #=======================================================================
    def plan_search(self, question: str) -> Dict[str, Any]:
        # Get relevant memory context for planning
        memory_context = self.tools.use_tool("memo_hybrid_search", query_text=question, top_k=5)
        
        # Parse image URLs from memory context
        image_urls = self._extract_image_urls(memory_context)

        # Planning prompt
        prompt = textwrap.dedent(f"""
            You are the PlanningAgent. Your job is to generate a concrete retrieval plan for how to gather information needed to answer the QUESTION.
            You must use the QUESTION and the current MEMORY (which contains abstracts of all messages so far).
            QUESTION: {question}
            MEMORY: {memory_context}
            AVAILABLE_IMAGE_URLS: {image_urls}

            PLANNING PROCEDURE
            1. Interpret the QUESTION using the context in MEMORY. Identify what information is needed to satisfy the QUESTION.
            2. Generate specific search queries for different retrieval approaches:
               - Use "keyword" for exact entities / functions / key attributes.
               - Use "vector" for conceptual understanding.
               - Use "hybrid" for comprehensive search combining both approaches.
               - Use "image" for direct visual question-answering when the QUESTION requires analyzing stored images.
            3. Create the queries:
               - "keyword_collection": a list of short keyword-style queries you will issue.
               - "vector_queries": a list of semantic / natural-language queries you will issue.
               - "hybrid_queries": a list of comprehensive queries combining keyword and semantic approaches.
               - "image_queries": a list of objects with "url" and "query" keys for specific image analysis.

            AVAILABLE RETRIEVAL TOOLS:
            All of the following retrieval tools are available to you. You may select one, several, or all of them in the same plan to maximize coverage. Parallel use of multiple tools is allowed and encouraged if it helps answer the QUESTION.
            1. "keyword"
               - WHAT IT DOES:
                 Exact keyword match retrieval over page content.
                 It finds pages that contain specific names, function names, key attributes, etc.
               - HOW TO USE:
                 Provide short, high-signal keywords.
                 Do NOT write long natural-language questions here. Use crisp keywords and phrases that should literally appear in relevant text.
            2. "vector"
               - WHAT IT DOES:
                 Semantic retrieval by meaning over page content.
                 It finds conceptually related pages.
                 This is good for high-level questions, reasoning questions, or "how/why" style questions.
               - HOW TO USE:
                 Write each query as a short natural-language sentence that clearly states what you want to know, using full context and entities from MEMORY and QUESTION.
                 Example style: "How does the memory system store and retrieve information?"
            3. "hybrid"
               - WHAT IT DOES:
                 Combined keyword and semantic retrieval over page content.
                 Provides comprehensive search results by leveraging both exact matches and conceptual similarity.
               - HOW TO USE:
                 Write queries that benefit from both approaches, typically for complex questions needing both specific details and broader context.
            4. "image"
               - WHAT IT DOES:
                 Direct visual question-answering over stored images.
                 Finds relevant images from memory and asks specific questions about their visual content.
                 Use this when the QUESTION requires visual analysis, identification, or detailed description of image content.
               - HOW TO USE:
                 Write specific questions about visual elements that can be answered by looking at images.
                 For each image query, specify both the image URL and the question to ask about that specific image.
                 Choose from AVAILABLE_IMAGE_URLS or specify URLs found in MEMORY.
                 Example format: {{"url": "https://example.com/image.jpg", "query": "What color is the fruit in this image?"}}

            RULES
            - Avoid simple repetition. Whether it's keywords or sentences for search, make them as independent as possible rather than duplicated.
            - Be specific. Avoid vague items like "get more details" or "research background".
            - Every string in "keyword_collection", "vector_queries", "hybrid_queries" must be directly usable as a retrieval query.
            - For "image_queries", each item must be an object with "url" and "query" keys containing the exact image URL and specific question.
            - For each image URL, it is critical that you do NOT modify or shorten the URL.
            - You may include multiple tools. Do NOT limit yourself to a single tool if more than one is useful.
            - Do NOT invent tools. Only use "keyword", "vector", "hybrid", "image".
            - You are only planning retrieval. Do NOT answer the QUESTION here.

            THINKING STEP
            - Before producing the output, think through the procedure and choices inside <think>...</think>.
            - Keep the <think> concise but sufficient to validate decisions.
            - After </think>, output ONLY the JSON object specified below. The <think> section must NOT be included in the JSON.

            OUTPUT JSON SPEC
            Return ONE JSON object with EXACTLY these keys:
            - "keyword_collection": array of strings (required)
            - "vector_queries": array of strings (required)
            - "hybrid_queries": array of strings (required)
            - "image_queries": array of objects with "url" and "query" keys (required)

            All keys MUST appear.
            After the <think> section, return ONLY the JSON object. Do NOT include any commentary or explanation outside the JSON.
            """).strip()

        try:
            response = self.tools.use_tool("generate_text", prompt=prompt)
            
            # Skip over the think section if it exists
            think_end_pattern = r'</think>\s*(.*)'
            think_match = re.search(think_end_pattern, response, re.DOTALL | re.IGNORECASE)
            
            if think_match:
                json_candidate = think_match.group(1).strip()
            else:
                json_candidate = response.strip()
            
            # Try to parse as JSON
            try:
                plan = json.loads(json_candidate)
            except json.JSONDecodeError:
                raise ValueError(f"Could not extract valid JSON from response: {json_candidate[:200]}...")

            plan.setdefault("keyword_collection", [])
            plan.setdefault("vector_queries", [])
            plan.setdefault("hybrid_queries", [])
            plan.setdefault("image_queries", [])

            return plan

        except Exception as e:
            print(f"Planning failed, using fallback: {e}")
            return {
                "keyword_collection": [],
                "vector_queries": [question],
                "hybrid_queries": [question],
                "image_queries": [],
            }


    #=======================================================================
    # Extracts image URLs from memory context
    #=======================================================================
    def _extract_image_urls(self, memory_context: str) -> List[str]:
        url_pattern = r'Image at URL ([^\s:]+):'
        urls = re.findall(url_pattern, memory_context)
        return list(set(urls))