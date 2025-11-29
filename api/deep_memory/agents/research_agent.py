from tools import Tools
from agents import PlanningAgent


#=======================================================================
# Agent for executing research queries over stored memories
#=======================================================================
class ResearchAgent:
    def __init__(self, tools: Tools):
        self.tools = tools
        self.planning_agent = PlanningAgent(tools)


    #=======================================================================
    # Performs deep research for a given query
    #=======================================================================
    def research(self, query: str) -> str:
        # Create and execute research plan
        plan = self.planning_agent.plan_search(query)
        search_results = {"keyword": [], "vector": [], "hybrid": [], "image": []}
        
        # Execute keyword searches
        for keyword_query in plan.get("keyword_collection", []):
            results = self.tools.use_tool("page_keyword_search", query_text=keyword_query, top_k=5)
            text_results = [item["text"] for item in results]
            search_results["keyword"].append({
                "query": keyword_query,
                "results": text_results
            })

        # Execute vector searches
        for vector_query in plan.get("vector_queries", []):
            results = self.tools.use_tool("page_vector_search", query_text=vector_query, top_k=5)
            text_results = [item["text"] for item in results]
            search_results["vector"].append({
                "query": vector_query,
                "results": text_results
            })

        # Execute hybrid searches
        for hybrid_query in plan.get("hybrid_queries", []):
            results = self.tools.use_tool("page_hybrid_search", query_text=hybrid_query, top_k=5)
            text_results = [item["text"] for item in results]
            search_results["hybrid"].append({
                "query": hybrid_query,
                "results": text_results
            })

        # Execute image queries
        for image_query_obj in plan.get("image_queries", []):
            image_url = image_query_obj["url"]
            question = image_query_obj["query"]
            
            try:
                answer = self.tools.use_tool("query_image", image_url=image_url, question=question)
                results = [answer]
            except Exception as e:
                results = [f"Could not query image - {e}"]
            
            search_results["image"].append({
                "query": f"{question}",
                "results": results
            })

        # Return compiled research
        answer = []
        for results in search_results.values():
            for result in results:
                answer.extend(result["results"])
        
        return "\n".join(answer)