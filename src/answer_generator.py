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
        # Fast lookup table
        # -----------------------------------

        self.node_lookup = {}

        for func in repo_index["functions"]:
            self.node_lookup[func["id"]] = func

        for cls in repo_index["classes"]:

            self.node_lookup[cls["id"]] = cls

            for method in cls["methods"]:
                self.node_lookup[method["id"]] = method

    def get_chunk_text(
            self,
            node_id
    ):

        node = self.node_lookup.get(node_id)

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

        retrieved_nodes = self.retriever.retrieve(
            query
        )

        # -----------------------------------
        # Better Context Assembly
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

            citations.append(node_id)

            code = self.get_chunk_text(
                node_id
            )

            context.append(
                f"""
ID: {node_id}

SOURCE:
{node['source']}

CODE:
{code}
"""
            )

        prompt = f"""
You are an expert software engineer performing codebase analysis.

Use ONLY the provided code context.
Semantic results are highly relevant.
Graph results are related dependencies.

If the answer cannot be determined from the context,
say so explicitly.

QUESTION

{query}

CODE CONTEXT

{chr(10).join(context)}

Instructions:

- Explain how the code actually works.
- Reference specific functions, methods, classes and files.
- Use code evidence whenever possible.
- Do not invent behavior not present in the code.
- Prefer concrete explanations over generic descriptions.

Special Rules:

For architecture questions:
- identify entry points
- identify major components
- identify data flow
- identify dependencies
- identify training and inference pipelines if present

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

        return answer