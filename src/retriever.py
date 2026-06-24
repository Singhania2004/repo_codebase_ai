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

        query_embedding = self.embedder.embed(query).tolist()

        results = self.vector_store.search(
            query_embedding,
            k
        )

        seeds = results["ids"][0]

        final_results = []

        # --------------------------------------------------
        # 1. Direct semantic matches first
        # --------------------------------------------------

        for node in seeds:

            if node not in final_results:
                final_results.append(node)

        # --------------------------------------------------
        # 2. Add callers
        # --------------------------------------------------

        for node in seeds:

            callers = self.analyzer.who_calls(node)

            for caller in callers:

                if caller not in final_results:
                    final_results.append(caller)

        # --------------------------------------------------
        # 3. Add callees
        # --------------------------------------------------

        for node in seeds:

            callees = self.analyzer.what_does_it_call(node)

            for callee in callees:

                if callee not in final_results:
                    final_results.append(callee)

        return final_results