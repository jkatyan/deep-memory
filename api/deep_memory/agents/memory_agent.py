from typing import List, Dict, Any
from tools import Tools
import uuid
import textwrap


#=======================================================================
# Agent for processing and storing memories
#=======================================================================
class MemoryAgent:
    def __init__(self, tools: Tools):
        self.tools = tools


    #=======================================================================
    # Processes and stores current memories in Pinecone
    #=======================================================================
    def process_memories(self, memories: List[Dict[str, Any]], context_window: str) -> None:
        for memory in memories:

            # Construct input message
            input_message = memory['text']
            input_message += " If there are any images associated with this message, their descriptions are as follows:"
            if memory['files']:
                input_message += " Associated images (preserve exact URLs):"
                for file_url in memory['files']:
                    try:
                        description = self.tools.use_tool("describe_image", image_url=file_url)
                        input_message += f" Image at URL {file_url}: {description}"
                    except Exception as e:
                        print(f"Warning: Could not describe image {file_url}: {e}")
                        input_message += f" Image at URL {file_url}: [Could not generate description - {e}]"
            else:
                input_message += " No images associated with this message."

            # Generate abstract using the generate_text tool
            abstract_prompt = textwrap.dedent(f"""
                Your job is to write one concise abstract that can be stored as long-term memory.

                MAIN OBJECTIVE:
                Generate a concise, self-contained and coherent abstract of INPUT_MESSAGE that preserves ALL important information in INPUT_MESSAGE.
                MEMORY_CONTEXT is provided so you can understand the broader situation such as people, modules, decisions, ongoing tasks and keep wording consistent.

                INPUTS:
                MEMORY_CONTEXT: {context_window}
                INPUT_MESSAGE: {input_message}

                YOUR TASK:
                1. Read INPUT_MESSAGE and extract all specific, memory-relevant information, such as:
                - plans, goals, decisions, requests, preferences
                - actions taken, next steps, assignments, and responsibilities
                - problems, blockers, bugs, questions that need follow-up
                - specific facts such as names, dates, numbers, locations
                2. Use MEMORY_CONTEXT to:
                - resolve or disambiguate the entities, components, tasks, or resources mentioned in INPUT_MESSAGE,
                - keep terminology (names of agents, modules, datasets, etc.) consistent with prior usage,
                - include minimal background context if it is required for the abstract to be understandable.
                You MUST NOT invent or add information that appears only in MEMORY_CONTEXT and is NOT implied or mentioned in INPUT_MESSAGE.
                3. Your abstract MUST:
                - summarize all important content from INPUT_MESSAGE,
                - include the EXACT URLs of all images mentioned in INPUT_MESSAGE (do not modify or shorten URLs),
                - summarize image contents while preserving their association with specific URLs,
                - be understandable on its own without seeing INPUT_MESSAGE,
                - be factual and specific.

                STYLE RULES:
                - Output exactly ONE concise paragraph. No bullet points.
                - Do NOT include meta phrases like "The user said..." or "The conversation is about...".
                - Do NOT give advice, opinions, or suggestions.
                - Do NOT ask questions.
                - Do NOT include anything that is not grounded in INPUT_MESSAGE.

                OUTPUT FORMAT:
                Return ONLY the single paragraph. Do NOT add any headings or labels.
                """).strip()

            abstract = self.tools.use_tool("generate_text", prompt=abstract_prompt)

            # Create and store records
            record_id = str(uuid.uuid4())

            # Store memo record (abstract)
            memo_record = {
                "_id": f"memo-{record_id}",
                "chunk_text": abstract
            }
            self.tools.use_tool("upsert_records", index_name="deep-memory-memo", records=[memo_record])
            self.tools.use_tool("upsert_records", index_name="deep-memory-memo-sparse", records=[memo_record])

            # Store page record (full content)
            page_record = {
                "_id": f"page-{record_id}",
                "chunk_text": memory['text'],
                "files": memory['files']
            }
            self.tools.use_tool("upsert_records", index_name="deep-memory-page", records=[page_record])
            self.tools.use_tool("upsert_records", index_name="deep-memory-page-sparse", records=[page_record])