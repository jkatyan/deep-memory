import json
import re
import textwrap
from ..tools import Tools


#=======================================================================
# Agent for integrating research evidence into factual summaries
#=======================================================================
class IntegrateAgent:
    def __init__(self, tools: Tools):
        self.tools = tools


    #=======================================================================
    # Integrates research evidence into a factual summary for a question
    #=======================================================================
    def integrate_evidence(self, question: str, evidence_context: str) -> str:
        # Integration prompt
        prompt = textwrap.dedent(f"""
            You are the IntegrateAgent. Your job is to build an integrated factual summary for a QUESTION.

            YOU ARE GIVEN:
            - QUESTION: what must be answered.
            - EVIDENCE_CONTEXT: newly retrieved supporting evidence that may contain facts relevant to the QUESTION.

            YOUR OBJECTIVE:
            Produce an UPDATED_RESULT that is a consolidated factual summary of all information that is relevant to the QUESTION.
            This is NOT a final answer to the QUESTION. It is an integrated summary of all useful facts that could be used to answer the QUESTION.

            The UPDATED_RESULT must:
            1. Add any new, relevant, well-supported facts from EVIDENCE_CONTEXT.
            2. Remove anything that is off-topic for the QUESTION.

            QUESTION: {question}
            EVIDENCE_CONTEXT: {evidence_context}

            INSTRUCTIONS:
            1. Understand the QUESTION. Identify exactly what needs to be answered.
            2. From EVIDENCE_CONTEXT:
               - Extract every fact that helps describe, clarify, or support an answer to the QUESTION.
               - Prefer concrete details such as entities, numbers, versions, decisions, timelines, outcomes, responsibilities, constraints.
               - Ignore anything unrelated to the QUESTION.
            3. Synthesis:
               - The merged text MUST read as one coherent factual summary related to the QUESTION (not the direct answer).
               - The merged summary MUST collect all important factual information needed to answer the QUESTION.
               - Do NOT add interpretation, recommendations, or conclusions beyond what is explicitly stated in EVIDENCE_CONTEXT.

            RULES:
            - "content" MUST ONLY include factual information that is relevant to the QUESTION.
            - You are NOT producing a final answer, decision, recommendation, or plan. You are producing a cleaned, merged factual summary.
            - Do NOT invent or infer facts that do not appear in EVIDENCE_CONTEXT.
            - Do NOT include meta language (e.g. "the evidence says", "according to RESULT", "the model stated").
            - Do NOT include instructions, reasoning steps, or analysis of your own process.
            - Do NOT include any keys other than "content".
            - "sources" should include the page_ids of the pages that supported the included facts.

            THINKING STEP
            - Before producing the output, think about selection and synthesis steps inside <think>...</think>.
            - Keep the <think> concise but sufficient to ensure correctness and relevance.
            - After </think>, output ONLY the JSON object. The <think> section must NOT be included in the JSON.

            OUTPUT JSON SPEC:
            Return ONE JSON object with EXACTLY:
            - "content": string. This is the UPDATED_RESULT, i.e. the integrated final information related to the QUESTION, if there not exist any useful information, just provide "".

            "content" MUST be present.
            After the <think> section, return ONLY the JSON object. Do NOT output Markdown, comments, headings, or explanations outside the JSON.
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
                result = json.loads(json_candidate)
                return result.get("content", "")
            except json.JSONDecodeError:
                raise ValueError(f"Could not extract valid JSON from response: {json_candidate[:200]}...")

        except Exception as e:
            print(f"Integration failed: {e}")
            return ""