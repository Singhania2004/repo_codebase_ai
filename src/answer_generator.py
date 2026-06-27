class AnswerGenerator:

    def __init__(
            self,
            retriever,
            repo_index,
            llm
    ):

        self.retriever = retriever
        self.repo_index = repo_index
        self.llm = llm

        # -----------------------------------
        # Conversation memory
        # -----------------------------------

        self.chat_history = []

        # -----------------------------------
        # Fast lookup table
        # -----------------------------------

        self.node_lookup = {}

        for func in repo_index["functions"]:
            self.node_lookup[
                func["id"]
            ] = func

        for cls in repo_index["classes"]:

            self.node_lookup[
                cls["id"]
            ] = cls

            for method in cls["methods"]:
                self.node_lookup[
                    method["id"]
                ] = method

    def get_chunk_text(
            self,
            node_id
    ):

        node = self.node_lookup.get(
            node_id
        )

        if not node:
            return ""

        return node.get(
            "source_code",
            ""
        )

    def answer(
            self,
            query
    ):

        # -----------------------------------
        # Retrieval history
        # -----------------------------------

        retrieval_query = query

        if self.chat_history:

            history_for_retrieval = ""

            for turn in self.chat_history[-2:]:

                history_for_retrieval += (
                    f"User: {turn['question']}\n"
                )

            retrieval_query = f"""
Previous conversation:

{history_for_retrieval}

Current question:

{query}
"""

        # -----------------------------------
        # Retrieve nodes
        # -----------------------------------

        retrieved_nodes = (
            self.retriever.retrieve(
                retrieval_query
            )
        )

        # -----------------------------------
        # Context assembly
        # -----------------------------------

        semantic_nodes = [
            n for n in retrieved_nodes
            if n["source"] == "semantic"
        ][:4]

        graph_nodes = [
            n for n in retrieved_nodes
            if n["source"] == "graph"
        ][:4]

        final_nodes = (
            semantic_nodes +
            graph_nodes
        )

        context = []

        citations = []

        for node in final_nodes:

            node_id = node["id"]

            citations.append(
                node_id
            )

            # Semantic nodes use Chroma chunk

            if (
                node["source"] == "semantic"
                and node.get("document")
            ):

                code = node["document"]

            # Graph nodes use lookup

            else:

                code = self.get_chunk_text(
                    node_id
                )

            context.append(
                f"""
ID: {node_id}

SOURCE:
{node['source']}

CONTENT:
{code}
"""
            )

        # -----------------------------------
        # Conversation history for LLM
        # -----------------------------------

        history_text = ""

        for turn in self.chat_history[-4:]:

            history_text += f"""
User:
{turn['question']}

Assistant:
{turn['answer']}
"""

        # -----------------------------------
        # Prompt
        # -----------------------------------

        prompt = f"""
You are an expert software engineer performing codebase analysis.

Use ONLY the provided code context.

Semantic results are highly relevant.

Graph results are supporting dependencies.

Conversation History:

{history_text}

Current Question:

{query}

If the current question refers to:
- it
- this
- that
- they
- those

use the conversation history to resolve the reference.

If the answer cannot be determined from the provided context,
say so explicitly.

CODE CONTEXT

{chr(10).join(context)}

Instructions:

- Explain how the code actually works.
- Reference specific functions, methods, classes and files.
- Use code evidence whenever possible.
- Do not invent behavior not present in the code.
- Prefer concrete explanations over generic descriptions.

For architecture questions:
- identify entry points
- identify major components
- identify data flow
- identify dependencies
- identify training and inference pipelines

For implementation questions:
- explain control flow
- explain function interactions
- explain important classes and methods

Output Format:

# Answer

<single detailed explanation>

# Relevant Code

- file.py::function
- file.py::Class.method

# Code Flow

<if applicable>

# Confidence

High / Medium / Low
"""

        answer = self.llm.generate(
            prompt
        )

        # -----------------------------------
        # Store history
        # -----------------------------------

        self.chat_history.append(
            {
                "question": query,
                "answer": answer[:1000]
            }
        )

        # Keep only recent conversations

        self.chat_history = (
            self.chat_history[-6:]
        )

        return answer