class HybridRetriever:

    def __init__(
            self,
            graph,
            analyzer,
            embedder,
            vector_store
    ):

        self.graph = graph
        self.analyzer = analyzer
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(
            self,
            query,
            k=5
    ):

        query_embedding = (
            self.embedder.embed(query).tolist()
        )

        results = self.vector_store.search(
            query_embedding,
            k
        )

        ids = results["ids"][0]
        distances = results["distances"][0]

        ranked = []

        for node_id, score in zip(ids, distances):

            ranked.append(
                {
                    "id": node_id,
                    "score": score,
                    "source": "semantic"
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
                            "source": "graph"
                        }
                    )

                    existing.add(neighbor)

        return ranked