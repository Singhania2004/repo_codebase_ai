class HybridRetriever:

    def __init__(
            self,
            graph,
            analyzer,
            embedder,
            vector_store,
            llm
    ):

        self.graph = graph
        self.analyzer = analyzer
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm = llm

    def retrieve(
            self,
            query,
            k=5
    ):

        rewritten = self.llm.rewrite_query(query)

        search_query = f"""
        Question:
        {query}

        Related concepts:
        {rewritten}
        """

        print("\nSearch Query:")
        print(search_query)

        query_embedding = (
            self.embedder.embed(
                search_query
            ).tolist()
        )

        results = self.vector_store.search(
            query_embedding,
            k
        )

        ids = results["ids"][0]
        distances = results["distances"][0]
        documents = results["documents"][0]

        ranked = []

        for node_id, score, document in zip(
                ids,
                distances,
                documents
        ):

            ranked.append(
                {
                    "id": node_id,
                    "score": score,
                    "source": "semantic",
                    "document": document
                }
            )

        existing = {
            item["id"]
            for item in ranked
        }

        for node in ids:

            callers = (
                self.analyzer.who_calls(node)
            )

            callees = (
                self.analyzer.what_does_it_call(node)
            )

            neighbors = callers + callees

            for neighbor in neighbors:

                if neighbor not in existing:

                    ranked.append(
                        {
                            "id": neighbor,
                            "score": 999,
                            "source": "graph",
                            "document": None
                        }
                    )

                    existing.add(neighbor)

        return ranked