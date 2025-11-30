from typing import List, Dict, Any, Optional
from .providers import OpenAIProvider, PineconeProvider
from .agents import ResearchAgent, MemoryAgent, IntegrateAgent
from .tools import Tools


#=======================================================================
# Deep memory system for storing and retrieving information
#=======================================================================
class DeepMemory:
    def __init__(
            self,
            pinecone_api_key: str,
            openai_api_key: str
        ):

        # API keys and configuration
        self.pinecone_api_key = pinecone_api_key
        self.openai_api_key = openai_api_key

        # Session memory storage
        self.memories: List[Dict[str, Any]] = []
        self.openai_provider = OpenAIProvider(self.openai_api_key)
        self.pinecone_provider = PineconeProvider(self.pinecone_api_key)

        # Initialize tools
        self.tools = Tools(self.pinecone_provider, self.openai_provider)

        # Initialize agents
        self.research_agent = ResearchAgent(self.tools)
        self.memory_agent = MemoryAgent(self.tools)
        self.integrate_agent = IntegrateAgent(self.tools)


    #=======================================================================
    # Adds a memory entry (text + optional files) to the session memory
    #=======================================================================
    def add_memory(self, text: str, files: Optional[List[str]] = None):
        self.memories.append({'text': text, 'files': files or []})


    #=======================================================================
    # Processes and stores current memories in Pinecone
    #=======================================================================
    def process_memories(self, context_window: str):
        self.memory_agent.process_memories(self.memories, context_window)
        self.memories = []


    #=======================================================================
    # Clears all memories from Pinecone indexes and local storage
    #=======================================================================
    def clear_memories(self):
        self.pinecone_provider.clear_all_indexes()
        self.memories = []


    #=======================================================================
    # Researches a query and returns a factual summary
    #=======================================================================
    def research(self, query: str) -> Dict[str, Any]:
        evidence_context = self.research_agent.research(query)
        
        # Integrate the evidence into a factual summary
        integrated_summary = self.integrate_agent.integrate_evidence(query, evidence_context)
        
        return integrated_summary