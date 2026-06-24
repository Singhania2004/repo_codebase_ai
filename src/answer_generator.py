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

    def get_chunk_text(
            self,
            node_id
    ):

        for func in self.repo_index["functions"]:

            if func["id"] == node_id:
                return func["source_code"]

        for cls in self.repo_index["classes"]:

            if cls["id"] == node_id:
                return cls["source_code"]

            for method in cls["methods"]:

                if method["id"] == node_id:
                    return method["source_code"]

        return ""

    def answer(
            self,
            query
    ):

        nodes = self.retriever.retrieve(query)

        context = []

        for node in nodes[:8]:

            code = self.get_chunk_text(node)

            context.append(
                f"""
ID: {node}

CODE:
{code}
"""
            )

        prompt = f"""
You are a senior software engineer.

Answer the question using only the provided code context.

QUESTION:
{query}

CONTEXT:
{chr(10).join(context)}

Provide:

1. Direct answer
2. Relevant files/functions
3. Short explanation
"""

        return self.llm.generate(prompt)